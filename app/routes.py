import base64
import json
import logging
import uuid
from datetime import datetime

from flask import request, render_template, url_for
from structlog import wrap_logger
from werkzeug.utils import redirect

from app import app
from app.messaging import message_manager
from app.tester import run_test
from app.read_data import extract_test_data

logger = wrap_logger(logging.getLogger(__name__))
tx_list = {}
responses = []


@app.route('/')
@app.route('/index')
def index():
    surveys = extract_test_data()
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
    result = run_test(message_manager, data_dict)
    responses.append(result)
    return redirect(url_for('index'))


@app.route('/response/<tx_id>', methods=['GET'])
def view_response(tx_id):
    for response in responses:
        if response.get_tx_id() == tx_id:
            b_dap_message = response.dap_message.data
            b_receipt = response.receipt.data

            if b_dap_message:
                dap_message = json.loads(b_dap_message.decode('utf-8'))
            else:
                dap_message = str(b_dap_message)
            if b_receipt:
                receipt = json.loads(b_receipt.decode('utf-8'))
            else:
                receipt = str(b_receipt)

            files = sort_response_files(response.files)
            return render_template('response.html',
                                   tx_id=tx_id,
                                   receipt=receipt,
                                   dap_message=dap_message,
                                   files=files)
        else:
            return render_template('response.html')


def sort_response_files(response_files: dict):
    sorted_files = {}
    for key, value in response_files.items():
        if key.lower().endswith(('jpg', 'png')):
            new_name = key.split(".")[-1]
            b64_image = base64.b64encode(value).decode()
            sorted_files[new_name] = b64_image
        else:
            sorted_files[key] = value.decode('utf-8')
    return sorted_files

