import logging
import uuid
import json
from flask import request, render_template, jsonify
from structlog import wrap_logger

from app import app
from app.messaging.manager import MessageManager
from app.tester import run_test
from app.read_data import extract_test_data

logger = wrap_logger(logging.getLogger(__name__))

message_manager = MessageManager()


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
    passed = run_test(message_manager, data_dict)
    return jsonify(passed)


def to_pretty_json(value):
    return json.dumps(value, sort_keys=True,
                      indent=4, separators=(',', ': '))


app.jinja_env.filters['tojson_pretty'] = to_pretty_json
