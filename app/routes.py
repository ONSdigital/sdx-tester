import base64
import enum
import json
import logging
import threading
import uuid
from datetime import datetime

from flask import request, render_template, url_for, flash
from structlog import wrap_logger
from werkzeug.utils import redirect

from app import app, socketio
from app.encryption import decrypt_survey
from app.messaging import message_manager
from app.tester import run_test
from app.read_data import extract_test_data_dict

logger = wrap_logger(logging.getLogger(__name__))

tx_list = {}
responses = []


class Messages(enum.Enum):
    In_progress = 0
    Unsuccessful = 1


@app.route('/')
@app.route('/index')
def index():
    surveys = extract_test_data_dict()
    return render_template('index.html',
                           surveys=surveys,
                           tx_list=tx_list)


@socketio.on('connect')
def make_ws_connection():
    print('Client Connected')


@app.route('/submit', methods=['POST'])
def submit():
    surveys = extract_test_data_dict()
    data_str = request.form.get('post-data')
    data_dict = json.loads(data_str)
    tx_id = str(uuid.uuid4())
    data_dict['tx_id'] = tx_id
    time_and_survey = f'({data_dict["survey_id"]})  {datetime.now().strftime("%H:%M")}'
    tx_list[time_and_survey] = tx_id
    threading.Thread(target=downstream_process, args=(data_dict,)).start()
    return render_template('index.html',
                           surveys=surveys,
                           tx_list=tx_list,
                           current_survey=data_str)


@app.route('/response/<tx_id>', methods=['GET'])
def view_response(tx_id):
    dap_message = Messages['In_progress'].value
    receipt = Messages['In_progress'].value
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


def downstream_process(data_dict: dict):
    result = run_test(message_manager, data_dict)
    responses.append(result)
    response = 'Emitting....'
    socketio.emit('data received', {'response': response})
    print('Emit data (websocket)')


def decode_files_and_images(response_files: dict):
    sorted_files = {}
    for key, value in response_files.items():
        if key.lower().endswith(('jpg', 'png')):
            b64_image = base64.b64encode(value).decode()
            sorted_files[key] = b64_image
        else:
            sorted_files[key] = value.decode('utf-8')
    return sorted_files


@app.template_filter()
def pretty_print(data):
    return json.dumps(data, indent=4)
