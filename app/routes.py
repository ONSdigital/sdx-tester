import json
import yaml

import uuid

import yaml
from flask import request, render_template, jsonify
from sdc.crypto.key_store import KeyStore
from sdc.crypto.encrypter import encrypt

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
    data = request.form.get('post-data')
    data_string = data.replace("'", '"')
    submission = json.loads(data_string)
    tx_id = str(uuid.uuid4())
    submission['tx_id'] = tx_id

    passed = run_test(submission, tx_id)
    return jsonify(passed)
