import json
import logging
import os
import threading
import uuid
import time
import structlog
import base64
from app import message_manager
from app.messaging.publisher import publish_dap_receipt
from app.tester import run_survey, run_seft
from datetime import datetime
from flask import request, render_template, flash
from app import app, socketio
from app.datastore.datastore_writer import cleanup_datastore
from app.jwt.encryption import decrypt_survey
from app.store import OUTPUT_BUCKET_NAME
from app.store.reader import check_file_exists
from app.survey_loader import get_json_surveys, read_ui
from app.result import Result

logger = structlog.get_logger()


# --------- Classes ----------


class UserSurveySubmissionsManager:
    """
    Keep control of the submitted
    surveys and their responses
    """
    def __init__(self):
        self.surveys = []

    def __iter__(self):
        """
        Make this object iterable
        and loop over each survey
        """
        for survey in self.surveys:
            yield survey

    def remove_survey(self, tx_id):
        """
        Remove a certain survey
        from this manager
        """
        for survey in list(self.surveys):
            if survey.tx_id == tx_id:
                return self.surveys.pop(survey)

    def process_survey(self, survey):
        """
        Store this survey in the class
        and then kick off a thread to process
        it
        """
        self.surveys.insert(0, survey)
        threading.Thread(target=survey.process_downstream_data).start()

    def get_response(self, tx_id):
        """
        Fetch a response for a user submitted
        survey given the tx_id
        """
        for survey in self.surveys:
            if survey.tx_id == tx_id:
                return survey.response

    def get_all_responses(self):
        return [survey.response for survey in self.surveys]


class UserSurveySubmission:
    """
    Class used for tracking
    a submission made by the
    user
    """
    def __init__(self, tx_id, survey_id, instrument_id, downstream_dict):
        self.tx_id = tx_id
        self.survey_id = survey_id
        self.instrument_id = instrument_id
        self.time_submitted = datetime.now().strftime("%H:%M")
        self.response = None
        self.downstream_dict = downstream_dict

    def process_downstream_data(self):
        """
        The function that processes the data for the submitted
        survey
        """
        self.response = run_survey(message_manager, self.downstream_dict)
        self._log_processed_survey()

    def _log_processed_survey(self):
        socketio.emit('data received', {'response': 'Emitting....'})
        logger.info('Emit data (websocket)')


class UserSeftSurveySubmission(UserSurveySubmission):
    """
    A child class used for SEFT submissions
    This class requires the
    downstream_dict -> the json response dictionary
    downstream_data -> the byte data for this SEFT
    """
    def __init__(self, tx_id, survey_id, instrument_id, downstream_dict, downstream_data):
        self.downstream_data = downstream_data
        UserSurveySubmission.__init__(self, f"seft_{tx_id}", survey_id, instrument_id, downstream_dict)

    def process_downstream_data(self):
        """
        The function that processes the data for a SEFT
        submission
        """
        self.response = run_seft(message_manager, self.downstream_dict, self.downstream_data)
        self._log_processed_survey()


# Track the submissions submitted by the user
submissions = UserSurveySubmissionsManager()


@app.get('/')
@app.get('/index')
def index():
    return render_template('index.html.j2',
                           survey_dict=get_json_surveys(),
                           submissions=submissions)


@socketio.on('connect')
def make_ws_connection():
    logging.info('Client Connected')


@socketio.on('dap_receipt')
def dap_receipt(tx_id):
    try:
        timeout = 0
        tx_id = tx_id['tx_id']
        file_path = post_dap_message(tx_id)

        while check_file_exists(file_path, OUTPUT_BUCKET_NAME) or timeout > 5:
            time.sleep(1)
            timeout += 1

        in_bucket = check_file_exists(file_path, OUTPUT_BUCKET_NAME)
        if not in_bucket:
            submissions.remove_survey(tx_id)
        socketio.emit('cleaning finished', {'tx_id': tx_id, 'in_bucket': in_bucket})

    except Exception as err:
        logger.error(f'Clean up process failed: {err}')
        socketio.emit('cleanup failed', {'tx_id': tx_id, 'error': err})


@socketio.on('collate')
def trigger_collate(data):
    """
    This function triggers a  kubernetes cronjob for sdx-collate
    """
    try:
        logger.info(data)
        os.system('kubectl create job --from=cronjob/sdx-collate test-collate')
        time.sleep(10)
        os.system('kubectl delete job test-collate')
        socketio.emit('Collate status', {'status': 'Successfully triggered sdx-collate'})
    except Exception as err:
        socketio.emit('Collate status', {'status': f'Collate failed to trigger: {err}'})


@socketio.on('cleanup datastore')
def trigger_cleanup_datastore():
    try:
        logger.info("Starting to clean Datastore")
        if cleanup_datastore():
            socketio.emit('Cleanup status', {'status': 'Datastore cleaned.'})
    except Exception as err:
        logger.error(f"Datastore wasn't cleaned error: {err}")


@app.post('/submit')
def submit():
    """
    Called when the user
    clicks the submit button
    after selecting a survey
    from the dropdown
    """

    # Read in surveys from disk
    surveys = read_ui()

    # Extract the current survey from the post request
    current_survey = request.form.get('post-data')
    # TODO if the user modifies the JSON to an invalid format this will fail
    data_dict = json.loads(current_survey)

    # TODO validate the json contains the required fields
    survey_id = data_dict["survey_id"]

    # Attempt to find an instrument ID
    try:
        instrument_id = data_dict["collection"]["instrument_id"]
    except KeyError:
        instrument_id = ""

    # Generate a tx_id
    tx_id = str(uuid.uuid4())
    data_dict['tx_id'] = tx_id

    if 'seft' in data_dict:
        byte_data = surveys[survey_id].get_seft_bytes()
        user_submission = UserSeftSurveySubmission(tx_id, survey_id, instrument_id, data_dict, byte_data)
    else:
        user_submission = UserSurveySubmission(tx_id, survey_id, instrument_id, data_dict)

    # Store this survey for later and process it in the background
    submissions.process_survey(user_submission)

    return render_template('index.html.j2',
                           submissions=submissions,
                           survey_dict = get_json_surveys(),
                           current_survey=current_survey,
                           number=survey_id)


@app.get('/response/<tx_id>')
def view_response(tx_id):
    """
    Called when the user clicks on the
    survey link after it's been
    submitted
    """

    dap_message = "In Progress"
    receipt = "In Progress"
    timeout = False
    quarantine = None
    files = {}
    errors = []

    # Fetch the response for the submitted survey
    response = submissions.get_response(tx_id)

    # Check the response has been found
    if response:
        timeout = response.timeout
        dap_message = response.dap_message
        receipt = response.receipt
        quarantine = response.quarantine
        errors = response.errors
        files = decode_files_and_images(response.files)

        if dap_message:
            dap_message = json.loads(dap_message.data.decode('utf-8'))

        if receipt:
            receipt = json.loads(receipt.data.decode('utf-8'))

        # TODO this line causes errors when quarantine is set to a string
        if quarantine:
            flash(f'Submission with tx_id: {tx_id} has been quarantined')
            if 'seft' not in response.quarantine.data.decode():
                quarantine = decrypt_survey(quarantine.data)
            else:
                quarantine = 'SEFT Quarantined'

        if timeout:
            flash('PubSub subscriber in sdx-tester timed out before receiving a response')

    return render_template('response.html.j2',
                           tx_id=tx_id,
                           receipt=receipt,
                           dap_message=dap_message,
                           files=files,
                           errors=errors,
                           quarantine=quarantine,
                           timeout=timeout)


@app.template_filter()
def pretty_print(data):
    """
    The indent parameter specifies how many spaces to indent by the data.
    """
    return json.dumps(data, indent=4)


# --------- Functions ----------


def downstream_process(*data):
    """
    For seft submissions, seft_name, seft_metadata and seft_bytes are required.
    """
    if len(data) > 1:
        result = run_seft(message_manager, data[0], data[1])
    else:
        result = run_survey(message_manager, data[0])
    submissions.add_response(result)
    response = 'Emitting....'
    socketio.emit('data received', {'response': response})
    logger.info('Emit data (websocket)')


def decode_files_and_images(response_files: dict):
    """
    For our tester we want to display the data that has been sent through our system. As SDX produces different
    file types they require different processing for our HTML page to display them correctly.
    """
    sorted_files = {}
    for key, value in response_files.items():
        if value is None:
            return response_files
        elif key == 'SEFT':
            return {key: 'Seft recieved'}
        elif key.lower().endswith(('jpg', 'png')):
            b64_image = base64.b64encode(value).decode()
            sorted_files[key] = b64_image
        elif type(value) is bytes:
            sorted_files[key] = value.decode('utf-8')
        else:
            sorted_files[key] = value
    return sorted_files


def post_dap_message(tx_id: str):
    timeout = 0
    while timeout < 30:
        for response in submissions.get_all_responses():
            if response.dap_message and tx_id == response.dap_message.attributes['tx_id']:
                file_path = response.dap_message.attributes['gcs.key']

                message_dict = json.loads(response.dap_message.data.decode())

                dap_message = {
                    'dataset': message_dict['dataset'] + '|' + file_path
                }
                publish_dap_receipt(dap_message)
                return file_path
        time.sleep(1)
        timeout += 1
    socketio.emit('cleanup failed', {'tx_id': tx_id, 'error': 'No response back from dap-topic'})
    return None




