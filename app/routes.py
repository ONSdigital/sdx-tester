import json
# import yaml
import pprint
import uuid

from flask import request, render_template
# from sdc.crypto.key_store import KeyStore
# from sdc.crypto.encrypter import encrypt

from app import app
from app.publish import publish_data
from app.read_data import extract_test_data


@app.route('/')
@app.route('/index')
def index():
    surveys = extract_test_data()
    # pprint.pprint(surveys)
    return render_template('index.html',
                           surveys=surveys)


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
    result = publish_data(payload)
    return render_template('result.html', tx_id=tx_id, result=result)
    # return render_template('result.html', tx_id=tx_id)
