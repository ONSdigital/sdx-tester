import copy
from datetime import datetime, date, timedelta

from app.messaging.publisher import publish_dap_receipt
from app.store import writer
from app.store.reader import check_file_exists, get_entity_count
from cleanup_tests import fake_surveys, input_files, dap_response
from cleanup_tests import output_files
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
    for data, filename in output_files.items():
        write_to_bucket(data, filename)

    for data, filename in input_files.items():
        write_to_bucket(data, filename)


def write_to_bucket(data, filename):
    bucket = filename.split('/', 1)[0]
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
    for data, filename in output_files.items():
        dap_message = copy.deepcopy(dap_response)
        dap_message['dataset'] = f"001|{filename.split('/', 1)[1]}"
        publish_dap_receipt(dap_message)


def have_files_been_deleted() -> bool:
    """
    Checks to see if all of the input and output files have been deleted from their respective buckets
    :return: True if they have been deleted, False otherwise.
    """
    deleted_outputs = are_deleted(output_files)
    if not deleted_outputs:
        return False

    deleted_inputs = are_deleted(input_files)
    if not deleted_inputs:
        return False

    return True


def are_deleted(files: dict) -> bool:
    """
    Have these files been deleted from the bucket

    :files: A dictionary of filenames to check. The filename must include the bucket and path.
    :return: True if they have been deleted, False otherwise.
    """
    for data, filename in files.items():
        bucket = filename.split('/', 1)[0]
        file_path = filename.split('/', 1)[1]
        exists = check_file_exists(file_path, bucket)
        if exists:
            return False
        else:
            print(f"{filename} has been deleted")

    return True


def is_datastore_cleaned_up() -> bool:
    for fake_id in fake_surveys:
        length = get_entity_count(fake_id + '_201605')
        return length < 1

