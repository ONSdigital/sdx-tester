import logging
import uuid
from flask import request, render_template, jsonify
from structlog import wrap_logger

from app import app
from app.messaging import message_manager
from app.tester import run_test
from app.read_data import extract_test_data

logger = wrap_logger(logging.getLogger(__name__))


@app.route('/')
@app.route('/index')
def index():
    surveys = extract_test_data()
    return render_template('index.html',
                           surveys=surveys)


@app.route('/submit', methods=['POST'])
def submit():
    data_str = request.form.get('post-data')
    data_dict = eval(data_str)
    tx_id = str(uuid.uuid4())
    data_dict['tx_id'] = tx_id
    result = run_test(message_manager, data_dict)
    passed = result.dap_message is not None
    return jsonify(passed)
