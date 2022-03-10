import io
import json
import os
import zipfile
import uuid
import time

from datetime import date, datetime, timedelta
from cryptography.fernet import Fernet
from google.cloud import storage, exceptions

from app.datastore.datastore_writer import write_entity, cleanup_datastore
from app.store.reader import does_comment_exist, get_comment_files
from comment_tests import surveys
from app.secret_manager import get_secret

PROJECT_ID = os.getenv('PROJECT_ID')
COMMENT_KEY = get_secret(PROJECT_ID, 'sdx-comment-key')
TIMEOUT = 150


def clean_datastore():
    cleanup_datastore()


def encrypt_comment(data: dict) -> str:
    comment_str = json.dumps(data)
    f = Fernet(COMMENT_KEY)
    token = f.encrypt(comment_str.encode())
    return token.decode()


def insert_comments():
    d = date.today()
    today = datetime(d.year, d.month, d.day)
    yesterday = today - timedelta(1)

    for survey_id in surveys:
        create_entity(survey_id, yesterday)

    # special creation of 134
    data_134 = {
        "created": yesterday,
        "encrypted_data": encrypt_comment({"ru_ref": "12346789012A",
                                           "boxes_selected": "91w, 95w, 96w, 97w, 91f, 95f, 96f, 97f, 191m, 195m, "
                                                             "196m, 197m, 191w4, 195w4, 196w4, 197w4, 191w5, 195w5, "
                                                             "196w5, 197w5, ",
                                           "comment": "flux clean",
                                           "additional": [{"qcode": "300w", "comment": "Pipe mania"},
                                                          {"qcode": "300f", "comment": "Gas leak"},
                                                          {"qcode": "300m", "comment": "copper pipe"},
                                                          {"qcode": "300w4", "comment": "solder joint"},
                                                          {"qcode": "300w5", "comment": "drill hole"}]}),
        "period": 201605,
        "survey_id": "134",
    }

    write_entity("134_201605", str(uuid.uuid4()), data_134, exclude_from_indexes=("encrypted_data",))


def create_entity(survey_id, date_stored):
    data = {
        "created": date_stored,
        "encrypted_data": encrypt_comment(
            {'ru_ref': '12346789012A', 'boxes_selected': '', 'comment': f'I am a {survey_id} comment',
             'additional': []}
        ),
        "period": 201605,
        "survey_id": survey_id,
    }

    write_entity(f"{survey_id}_201605", str(uuid.uuid4()), data, exclude_from_indexes=("encrypted_data",))


def bucket_cleanup():
    try:
        bucket_name = f'{PROJECT_ID}-outputs'
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix='comments')
        for blob in blobs:
            blob.delete()
            print(f"Blob: {blob} deleted.")
    except exceptions.NotFound as error:
        print(error)


def wait_for_comments():
    count = 0
    while not does_comment_exist() and count < TIMEOUT:
        print('SDX-Collate waiting for resources. Waiting 20 seconds...')
        time.sleep(20)
        count += 20


def extract_files():
    result = get_comment_files()
    z = zipfile.ZipFile(io.BytesIO(result), "r")
    z.extractall('temp_files')
