import json
import uuid

from flask import request, render_template, jsonify
from app import app
from app.tester import run_test
from app.read_data import extract_test_data


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
    passed = run_test(data_dict, tx_id)
    return jsonify(passed)
