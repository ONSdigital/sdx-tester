import base64

import json
import logging
import threading
import uuid
from datetime import datetime

from flask import request, render_template, flash, session
from structlog import wrap_logger

from app import app, socketio
from app.jwt.encryption import decrypt_survey
from app.messaging import message_manager
from app.messaging.publisher import publish_dap_receipt
from app.survey_loader import read_UI
from app.tester import run_survey, run_seft

logger = wrap_logger(logging.getLogger(__name__))

submissions = []
responses = []


@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    test_data = read_UI()
    return render_template('index.html',
                           surveys=test_data,
                           number='-- Choose a Survey_ID --',
                           submissions=submissions)


@socketio.on('connect')
def make_ws_connection():
    logging.info('Client Connected')


@socketio.on('dap_receipt')
def dap_receipt(tx_id):
    post_dap_message(tx_id)
    socketio.emit(f"Clean up triggered for {tx_id['tx_id']}")


@app.route('/submit', methods=['POST'])
def submit():
    downstream_data = []
    surveys = read_UI()
    survey = request.form.get('post-data')

    data_dict = json.loads(survey)
    survey_id = data_dict["survey_id"]

    tx_id = str(uuid.uuid4())
    data_dict['tx_id'] = tx_id
    downstream_data.append(data_dict)

    if 'seft' in data_dict:
        seft_submission = surveys[f'seft_{survey_id}']
        data_bytes = seft_submission.get_seft_bytes()
        downstream_data.append(data_bytes)
        survey_id = 'seft_' + survey_id

    time_and_survey = {f'({survey_id})  {datetime.now().strftime("%H:%M")}': tx_id}
    submissions.insert(0, time_and_survey)

    threading.Thread(target=downstream_process, args=tuple(downstream_data)).start()

    return render_template('index.html',
                           surveys=surveys,
                           submissions=submissions[:20],
                           current_survey=survey,
                           number=survey_id)


@app.route('/response/<tx_id>', methods=['GET'])
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
                quarantine = decrypt_survey(quarantine.data)

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


def post_dap_message(tx_id: dict):
    for response in responses:
        if response.dap_message and tx_id['tx_id'] == response.dap_message.attributes['tx_id']:
            dap_message = {
                'data': response.dap_message.data,
                'ordering_key': '',
                'attributes': {
                    "gcs.bucket": response.dap_message.attributes['gcs.bucket'],
                    "gcs.key": response.dap_message.attributes['gcs.key']
                }
            }
            publish_dap_receipt(dap_message, tx_id['tx_id'])


@app.template_filter()
def pretty_print(data):
    return json.dumps(data, indent=4)
