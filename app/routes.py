import json
import yaml
import uuid

from flask import request, render_template
from sdc.crypto.key_store import KeyStore
from sdc.crypto.encrypter import encrypt

from app import app
from app.publish import publish_data


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.get('post-data')
    submission = json.loads(data)
    tx_id = '12345'
    submission['tx_id'] = str(uuid.uuid4())

    with open("./keys.yml") as file:
        secrets_from_file = yaml.safe_load(file)

    key_store = KeyStore(secrets_from_file)
    payload = encrypt(submission, key_store, 'submission')

    result = publish_data(payload)
    return render_template('result.html', tx_id=tx_id, result=result)
