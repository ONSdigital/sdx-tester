import base64
import json
import logging
import os
import threading
import uuid
import time
import structlog

from datetime import datetime
from flask import request, render_template, flash
from app import app, socketio
from app.jwt.encryption import decrypt_survey
from app import message_manager
from app.messaging.publisher import publish_dap_receipt
from app.store import OUTPUT_BUCKET_NAME
from app.store.reader import check_file_exists
from app.survey_loader import read_ui
from app.tester import run_survey, run_seft

logger = structlog.get_logger()

submissions = []
responses = []


@app.get('/')
@app.get('/index')
def index():
    test_data = read_ui()
    return render_template('index.html',
                           surveys=test_data,
                           number='-- Choose a Survey_ID --',
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
            remove_submissions(tx_id)
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


@app.post('/submit')
def submit():
    downstream_data = []
    surveys = read_ui()
    current_survey = request.form.get('post-data')

    data_dict = json.loads(current_survey)
    survey_id = data_dict["survey_id"]

    tx_id = str(uuid.uuid4())
    data_dict['tx_id'] = tx_id
    downstream_data.append(data_dict)

    if 'seft' in data_dict:
        # To distinguish seft submissions, their survey ids are displayed in the form of 'seft_(survey_id)'.
        seft_submission = surveys[f'seft_{survey_id}']
        data_bytes = seft_submission.get_seft_bytes()
        downstream_data.append(data_bytes)
        survey_id = 'seft_' + survey_id

    time_and_survey = {tx_id: f'({survey_id})  {datetime.now().strftime("%H:%M")}'}
    submissions.insert(0, time_and_survey)

    threading.Thread(target=downstream_process, args=tuple(downstream_data)).start()

    return render_template('index.html',
                           surveys=surveys,
                           submissions=submissions[:15],
                           current_survey=current_survey,
                           number=survey_id)


@app.get('/response/<tx_id>')
def view_response(tx_id):
    dap_message = "In Progress"
    receipt = "In Progress"
    timeout = False
    quarantine = None
    files = {}
    errors = []
    for response in responses:
        if response.get_tx_id() == tx_id:
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
                flash(f'Submission with tx_id: {quarantine.attributes["tx_id"]} has been quarantined')
                if 'seft' not in response.quarantine.data.decode():
                    quarantine = decrypt_survey(quarantine.data)
                else:
                    quarantine = 'SEFT Quarantined'

            if timeout:
                flash('PubSub subscriber in sdx-tester timed out before receiving a response')

            return render_template('response.html',
                                   tx_id=tx_id,
                                   receipt=receipt,
                                   dap_message=dap_message,
                                   files=files,
                                   errors=errors,
                                   quarantine=quarantine,
                                   timeout=timeout)
    return render_template('response.html',
                           tx_id=tx_id,
                           receipt=receipt,
                           dap_message=dap_message,
                           files=files,
                           errors=errors,
                           quarantine=quarantine,
                           timeout=timeout)


def downstream_process(*data):
    """
    For seft submissions, seft_name, seft_metadata and seft_bytes are required.
    """
    if len(data) > 1:
        result = run_seft(message_manager, data[0], data[1])
    else:
        result = run_survey(message_manager, data[0])
    responses.append(result)
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
        for response in responses:
            if response.dap_message and tx_id == response.dap_message.attributes['tx_id']:
                file_path = response.dap_message.attributes['gcs.key']
                dap_message = {
                    'data': response.dap_message.data,
                    'ordering_key': '',
                    'attributes': {
                        "gcs.bucket": response.dap_message.attributes['gcs.bucket'],
                        "gcs.key": response.dap_message.attributes['gcs.key']
                    }
                }
                publish_dap_receipt(dap_message, tx_id)
                return file_path
        time.sleep(1)
        timeout += 1
    socketio.emit('cleanup failed', {'tx_id': tx_id, 'error': 'No response back from dap-topic'})
    return None


def remove_submissions(tx_id):
    for submission in submissions:
        for key in submission.keys():
            if tx_id == key:
                submissions.remove(submission)


@app.template_filter()
def pretty_print(data):
    """
    The indent parameter specifies how many spaces to indent by the data.
    """
    return json.dumps(data, indent=4)
