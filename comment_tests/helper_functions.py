import json
import os
import time
import uuid
from datetime import date, datetime, timedelta

from cryptography.fernet import Fernet
from google.cloud import datastore, storage, exceptions
from comment_tests import surveys

PROJECT_ID = os.getenv('PROJECT_ID')
datastore_client = datastore.Client(project=PROJECT_ID)
COMMENT_KEY = "E3rjFT2i9ALcvc99Pe3YqjIGrzm3LdMsCXc8nUaOEbc="
TIMEOUT = 150


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

    survey_134 = datastore.Entity(datastore_client.key("134_201605", str(uuid.uuid4())))

    survey_134.update(
        {
            "created": yesterday,
            "encrypted_data": encrypt_comment({"ru_ref": "12346789012A",
                                               "boxes_selected": "91w, 95w, 96w, 97w, 91f, 95f, 96f, 97f, 191m, 195m, 196m, 197m, 191w4, 195w4, 196w4, 197w4, 191w5, 195w5, 196w5, 197w5, ",
                                               "comment": "flux clean",
                                               "additional": [{"qcode": "300w", "comment": "Pipe mania"},
                                                              {"qcode": "300f", "comment": "Gas leak"},
                                                              {"qcode": "300m", "comment": "copper pipe"},
                                                              {"qcode": "300w4", "comment": "solder joint"},
                                                              {"qcode": "300w5", "comment": "drill hole"}]}),
            "period": 201605,
            "survey_id": "134",
        }
    )
    datastore_client.put(survey_134)

    print(f'Successfully put 134 into Datastore')


def create_entity(survey_id, date_stored):
    survey_entity = datastore.Entity(datastore_client.key(f"{survey_id}_201605", str(uuid.uuid4())))

    survey_entity.update(
        {
            "created": date_stored,
            "encrypted_data": encrypt_comment(
                {'ru_ref': '12346789012A', 'boxes_selected': '', 'comment': f'I am a {survey_id} comment',
                 'additional': []}
            ),
            "period": 201605,
            "survey_id": survey_id,
        }
    )
    datastore_client.put(survey_entity)
    print(f'Successfully put {survey_id} into Datastore')


def cleanup_datastore():
    try:
        kinds = fetch_comment_kinds()
        for kind in kinds:
            query = datastore_client.query(kind=kind)
            query.keys_only()
            keys = [entity.key for entity in query.fetch()]
            datastore_client.delete_multi(keys)
            print(f'successfully deleted {keys} from Datastore')

    except Exception as e:
        print(e)
        print('Failed to delete item from Datastore')
    return True


def fetch_comment_kinds() -> list:
    """
        Fetch a list of all comment kinds from datastore.
        Each kind is represented by {survey_id}_{period}
    """
    try:
        query = datastore_client.query(kind="__kind__")
        query.keys_only()
        return [entity.key.id_or_name for entity in query.fetch() if not entity.key.id_or_name.startswith("_")]
    except Exception as e:
        print(f'Datastore error fetching kinds: {e}')
        raise e


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
