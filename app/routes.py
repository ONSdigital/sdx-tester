import json
# import yaml
import uuid

from flask import request, render_template, jsonify
# from sdc.crypto.key_store import KeyStore
# from sdc.crypto.encrypter import encrypt

from app import app
from app.tester import run_test


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.get('post-data')
    submission = json.loads(data)
    tx_id = str(uuid.uuid4())
    submission['tx_id'] = tx_id

    # with open("./keys.yml") as file:
    #     secrets_from_file = yaml.safe_load(file)
    #
    # key_store = KeyStore(secrets_from_file)
    # payload = encrypt(submission, key_store, 'submission')
    #
    payload = json.dumps(submission)
    passed = run_test(payload, tx_id)
    return jsonify(passed)
