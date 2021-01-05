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


@app.route('/')
@app.route('/index')
def index():
    surveys = extract_test_data()
    print(tx_list)
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
    passed = result.dap_message is not None
    return redirect(url_for('index'))


@app.route('/response/<tx_id>', methods=['GET'])
def view_response(tx_id):
    return render_template('response.html',
                           tx_id=tx_id)
