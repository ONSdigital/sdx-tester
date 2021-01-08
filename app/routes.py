import base64
import json
import logging
import threading
import uuid
from datetime import datetime

from flask import request, render_template, url_for
from structlog import wrap_logger
from werkzeug.utils import redirect

from app import app, socketio
from app.messaging import message_manager
from app.tester import run_test
from app.read_data import extract_test_data_dict

logger = wrap_logger(logging.getLogger(__name__))

tx_list = {}
responses = []


@app.route('/')
@app.route('/index')
def index():
    surveys = extract_test_data_dict()
    return render_template('index.html',
                           surveys=surveys,
                           tx_list=tx_list)


@app.route('/submit', methods=['POST'])
def submit():
    data_str = request.form.get('post-data')
    data_dict = json.loads(data_str)
    tx_id = str(uuid.uuid4())
    data_dict['tx_id'] = tx_id
    time = datetime.now()
    time = time.strftime("%H:%M:%S")
    tx_list[time] = tx_id
    threading.Thread(target=new_thread_for_response, args=(data_dict,)).start()
    return redirect(url_for('index'))


@app.route('/response/<tx_id>', methods=['GET'])
def view_response(tx_id):
    dap_message = None
    receipt = None
    quarantine = None
    files = {}
    errors = []
    for response in responses:
        if response.get_tx_id() == tx_id:
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
                receipt = json.loads(quarantine.data.decode('utf-8'))

            return render_template('response.html',
                                   tx_id=tx_id,
                                   receipt=receipt,
                                   dap_message=dap_message,
                                   files=files,
                                   errors=errors,
                                   quarantine=quarantine)
    return render_template('response.html',
                           tx_id=tx_id,
                           receipt=receipt,
                           dap_message=dap_message,
                           files=files,
                           errors=errors,
                           quarantine=quarantine)


@socketio.on('connect')
def make_ws_connection():
    print('Client Connected')


def new_thread_for_response(data_dict: dict):
    result = run_test(message_manager, data_dict)
    responses.append(result)
    response = 'Emitting....'


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
