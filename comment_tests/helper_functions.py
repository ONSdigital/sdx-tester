import io
import zipfile
import uuid
import time

from datetime import date, datetime, timedelta
from google.cloud import storage, exceptions
from typing import List

from app import PROJECT_ID
from app.datastore.datastore_writer import write_entity, cleanup_datastore, encrypt_comment
from app.store.reader import does_comment_exist, get_comment_files
from comment_tests import surveys


TIMEOUT = 300


def clean_datastore():
    cleanup_datastore()


def get_datetime(no_days_previous: int):
    d = date.today()
    today = datetime(d.year, d.month, d.day)
    return today - timedelta(no_days_previous)


def insert_comments(survey_id_list: List[str], period, date_created: datetime):

    for survey_id in survey_id_list:
        insert_comment(survey_id, period, date_created)


def insert_comment(survey_id: str, period: str, date_stored: datetime):
    data = {
        "created": date_stored,
        "encrypted_data": encrypt_comment(
            {'ru_ref': '12346789012A', 'boxes_selected': '', 'comment': f'I am a {survey_id} comment',
             'additional': []}
        )
    }

    write_entity(f"{survey_id}_{period}", str(uuid.uuid4()), data, exclude_from_indexes=("encrypted_data",))


def create_comments():

    yesterday = get_datetime(1)

    insert_comments(surveys, '201605', yesterday)

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
                                                          {"qcode": "300w5", "comment": "drill hole"}]})
    }

    write_entity("134_201605", str(uuid.uuid4()), data_134, exclude_from_indexes=("encrypted_data",))


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
