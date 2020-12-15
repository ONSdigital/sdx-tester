import json
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
    return render_template('index.html',
                           surveys=surveys)


@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.get('post-data')
    data_string = data.replace("'", '"')
    data_dict = json.loads(data_string)
    tx_id = str(uuid.uuid4())
    data_dict['tx_id'] = tx_id

    print('converting to json....')
    payload = json.dumps(data_dict)
    result = publish_data(payload)
    return render_template('result.html',
                           tx_id=tx_id,
                           result=result)

