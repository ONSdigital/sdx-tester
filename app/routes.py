import json
import logging
import os
import uuid
import time
import structlog
from app.messaging.publisher import publish_dap_receipt
from app.tester import UserSurveySubmissionsManager, UserSurveySubmission, UserSeftSurveySubmission, \
    decode_files_and_images
from flask import request, render_template, flash
from app import app, socketio, CONFIG
from app.datastore.datastore_writer import cleanup_datastore
from app.jwt.encryption import decrypt_survey
from app.store import OUTPUT_BUCKET_NAME
from app.store.reader import check_file_exists
from app.survey_loader import SurveyLoader, Survey, InvalidSurveyException, Seft

logger = structlog.get_logger()

# logging.getLogger('werkzeug').disabled = True # (Use this to disable constant console logs)

# Track the submissions submitted by the user
submissions = UserSurveySubmissionsManager()

# Survey loader
survey_loader = SurveyLoader(CONFIG.DATA_FOLDER)


@app.get('/')
@app.get('/index')
def index():
    a = survey_loader.to_json()
    return render_template('index.html.j2',
                           survey_dict=survey_loader.to_json(),
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

    # Extract the current survey from the post request
    current_survey = request.form.get('post-data')

    # First we check if the json is valid format
    try:
        data_dict = json.loads(current_survey)
    except json.decoder.JSONDecodeError:
        flash("Invalid JSON format")
    else:

        # Update current_survey variable to avoid rendering issue
        current_survey = data_dict

        # Generate a random tx_id
        tx_id = str(uuid.uuid4())
        # Update the data dict with the new tx_id
        data_dict["tx_id"] = tx_id

        # Seft
        if "seft" in data_dict:
            try:
                current_survey = Seft(data_dict)
            except InvalidSurveyException as e:
                flash(e.message)
            else:
                byte_data = current_survey.byte_data
                instrument_id = ""
                # Create and process the survey submission
                submissions.process_survey(UserSeftSurveySubmission(tx_id,
                                                           current_survey.survey_id,
                                                           instrument_id, data_dict,
                                                           byte_data ))

        # Non seft
        else:
            try:
                current_survey = Survey(data_dict)
            except InvalidSurveyException as e:
                flash(e.message)
            else:
                try:
                    # Create and process the survey submission
                    submissions.process_survey(UserSurveySubmission(tx_id,
                                                                    current_survey.survey_id,
                                                                    current_survey.extract_form_type(),
                                                                    data_dict))
                except InvalidSurveyException as e:
                    flash(e.message)

    # Attempt to serialize before returning
    if type(current_survey) is Survey:
        current_survey = current_survey.serialize()

    # Render the ui
    return render_template('index.html.j2',
                           submissions=submissions,
                           survey_dict=survey_loader.to_json(),
                           current_survey=current_survey,
                           )


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

        if quarantine:
            flash(f'Submission with tx_id: {tx_id} has been quarantined')

            # SEFT quarantine data is different so we need to check it's attributes so the app doesnt crash
            if hasattr(quarantine, 'data'):

                if 'seft' not in response.quarantine.data.decode():
                    quarantine = decrypt_survey(quarantine.data)
                else:
                    quarantine = 'SEFT Quarantined'
            elif type(quarantine) is not str:
                quarantine = "Survey Quarantined"

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
    if data:
        return json.dumps(data, indent=4)
    return ""


# --------- Functions ----------

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




