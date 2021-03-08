import base64
import hashlib
import json
import logging
import threading
import uuid
from datetime import datetime

from flask import request, render_template, flash
from structlog import wrap_logger

from app import app, socketio, survey_loader
from app.jwt.encryption import decrypt_survey
from app.messaging import message_manager
from app.tester import run_survey, run_seft

logger = wrap_logger(logging.getLogger(__name__))

submissions = []
responses = []


@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    surveys = survey_loader.read_all()
    return render_template('index.html',
                           surveys=surveys,
                           submissions=submissions)


@socketio.on('connect')
def make_ws_connection():
    print('Client Connected')


@app.route('/submit', methods=['POST'])
def submit():
    surveys = survey_loader.read_all()
    data_str = request.form.get('post-data')
    print(data_str)
    print(type(data_str))
    # name = data.split(' ')[0]
    # data_str = data.split(' ', 1)[1]
    # print(data_str)
    if 'type' in data_str:
        data_dict = json.loads(data_str)
        number = data_dict["survey_id"]
        tx_id = str(uuid.uuid4())
        data_dict['tx_id'] = tx_id
        time_and_survey = {f'({number})  {datetime.now().strftime("%H:%M")}': tx_id}
        submissions.insert(0, time_and_survey)
        threading.Thread(target=survey_downstream_process, args=(data_dict,)).start()
        return render_template('index.html',
                               surveys=surveys,
                               submissions=submissions,
                               current_survey=data_str,
                               number=number)
    else:
        # submit_seft(surveys, data_str)
        data_bytes = bytes(data_str, 'UTF-8')
        data_dict = json.loads(data_str)
        print(data_dict)
        number = data_dict["survey_id"]
        print(number)
        tx_id = data_dict["tx_id"]
        print(tx_id)
        time_and_survey = {f'(seft_{number})  {datetime.now().strftime("%H:%M")}': tx_id}
        submissions.insert(0, time_and_survey)
        threading.Thread(target=seft_downstream_process, args=(data_dict, data_bytes,)).start()
        return render_template('index.html',
                               surveys=surveys,
                               submissions=submissions,
                               current_survey=data_str,
                               number='seft_' + number)


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


def survey_downstream_process(data_dict: dict):
    result = run_survey(message_manager, data_dict)
    responses.append(result)
    response = 'Emitting....'
    socketio.emit('data received', {'response': response})
    print('Emit data (websocket)')


def seft_downstream_process(message, data_bytes):
    result = run_seft(message_manager, message, data_bytes)
    responses.append(result)
    response = 'Emitting....'
    socketio.emit('data received', {'response': response})
    print('Emit data (websocket)')


def decode_files_and_images(response_files: dict):
    sorted_files = {}
    for key, value in response_files.items():
        if value is None:
            return response_files
        elif key.lower().endswith(('jpg', 'png')):
            b64_image = base64.b64encode(value).decode()
            sorted_files[key] = b64_image
        elif type(value) is bytes:
            sorted_files[key] = value.decode('utf-8')
        else:
            sorted_files[key] = value
    return sorted_files


@app.template_filter()
def pretty_print(data):
    return json.dumps(data, indent=4)
