import json
from datetime import datetime, date, timedelta

from app.messaging.publisher import publish_dap_receipt
from app.store import writer
from app.store.reader import check_file_exists, get_entity_count
from cleanup_tests import fake_surveys
from cleanup_tests import test_data
from comment_tests.helper_functions import create_entity

"""
This file contains functions that insert data into both buckets and Datastore and then publishes a message onto
dap-receipt-topic. This should trigger the sdx-cleanup cloud function to then clean up the data we have inserted.
test_cleanup.py then runs queries to check if the data has in fact been deleted.
"""


def setup_output_bucket():
    """
    Upload data to buckets in ons-sdx-{{project_id}}
    """
    for data, filename in test_data.items():
        bucket = filename.split('/', 1)[0]
        if data == "seft-input":
            filename = filename.split('/')[2]
        else:
            filename = filename.split('/', 1)[1]
        writer.write(data, filename, bucket)
        print(f'Successfully put data in {bucket}/{filename}')


def setup_comments():
    """
    Upload 5 comments to Datastore in ons-sdx-{{project_id}}
    """
    d = date.today()
    today = datetime(d.year, d.month, d.day)
    ninety_days_ago = today - timedelta(days=91)
    for fake_id in fake_surveys:
        create_entity(fake_id, ninety_days_ago)


def kickoff_cleanup_outputs():
    """
    Publishes a PuSub message for each element placed within the bucket.
    """
    test_data.pop('seft-input')
    for data, filename in test_data.items():
        dap_message = {'dataset': f"009|{filename.split('/', 1)[1]}"}
        publish_dap_receipt(dap_message)


def is_bucket_empty() -> bool:
    for data, filename in test_data.items():
        bucket = filename.split('/', 1)[0]
        file_path = filename.split('/', 1)[1]
        return not check_file_exists(file_path, bucket)


def is_datastore_cleaned_up() -> bool:
    for fake_id in fake_surveys:
        length = get_entity_count(fake_id + '_201605')
        return length < 1

