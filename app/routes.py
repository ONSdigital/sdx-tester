import logging
import uuid
from flask import request, render_template, jsonify
from structlog import wrap_logger

from app import app
from app.messaging import message_manager
from app.tester import run_test
from app.read_data import extract_test_data

logger = wrap_logger(logging.getLogger(__name__))
tx_list = ["40e659ec-013f-4993-9a31-ec1e0ad37888", "9db49fb8-4bcc-4615-b42c-b2ab80b234b8",
           "d6d7acf4-52f4-41f6-83b1-c0806904ca42", "308409e4-cf09-46cb-8988-f85e7116ade6",
           "b7f78b30-1814-45ac-963d-8c997c091f90"]


@app.route('/')
@app.route('/index')
def index():
    surveys = extract_test_data()
    return render_template('index.html',
                           surveys=surveys,
                           tx_list=tx_list)


@app.route('/submit', methods=['POST'])
def submit():
    surveys = extract_test_data()
    data_str = request.form.get('post-data')
    data_dict = eval(data_str)
    tx_id = str(uuid.uuid4())
    data_dict['tx_id'] = tx_id
    tx_list.append(tx_id)
    result = run_test(message_manager, data_dict)
    passed = result.dap_message is not None
    print(passed)
    return render_template('index.html',
                           surveys=surveys,
                           tx_list=tx_id)
