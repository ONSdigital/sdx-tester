import copy
import uuid
import time
from datetime import datetime, date, timedelta

from app import PROJECT_ID
from app.datastore.datastore_writer import encrypt_comment, write_entity
from app.jwt.encryption import encrypt_survey
from app.messaging.publisher import publish_dap_receipt
from app.store import writer, OUTPUT_BUCKET_NAME
from app.store.reader import check_file_exists
from app.datastore.datastore_reader import get_entity_count
from app.store.writer import write
from cleanup_tests import fake_surveys, input_files, dap_response
from cleanup_tests import output_mock_files
from google.cloud import storage

"""
This file contains functions that insert data into both buckets and Datastore and then publishes a message onto
dap-receipt-topic. This should trigger the sdx-cleanup cloud function to then clean up the data we have inserted.
test_cleanup.py then runs queries to check if the data has in fact been deleted.
"""

MAX_TIMEOUT_IN_SECONDS = 60


def setup_input_and_output_buckets():
    """
    Upload data to buckets in ons-sdx-{{project_id}}
    """

    for filename, data in input_files.items():
        write_to_bucket(data, filename)

    for filename, data in output_mock_files.items():
        write_to_bucket(data, filename)


def write_to_bucket(data, filename):
    bucket = filename.split('/', 1)[0]
    encrypted_survey = encrypt_survey(data)
    output_filename = filename.split('/', 1)[1]
    write(encrypted_survey, output_filename, bucket)


def setup_comments():
    """
    Upload 5 comments to Datastore in ons-sdx-{{project_id}}
    """
    d = date.today()
    today = datetime(d.year, d.month, d.day)
    ninety_days_ago = today - timedelta(days=91)
    for fake_id in fake_surveys:
        insert_comment(fake_id, ninety_days_ago)


def insert_comment(survey_id, date_stored):
    data = {
        "created": date_stored,
        "encrypted_data": encrypt_comment(
            {'ru_ref': '12346789012A', 'boxes_selected': '', 'comment': f'I am a {survey_id} comment',
             'additional': []}
        )
    }

    write_entity(f"{survey_id}_201605", str(uuid.uuid4()), data, exclude_from_indexes=("encrypted_data",))


def kickoff_cleanup_outputs(files_in_output_bucket: list[str]):
    """
    Publishes a PuSub message for each element placed within the bucket.
    """
    for filename in files_in_output_bucket:
        dap_message = copy.deepcopy(dap_response)
        print(f"{filename} is the filename")
        file = f"001|{filename}"
        print(file)
        dap_message['dataset'] = file
        publish_dap_receipt(dap_message)


def have_files_been_deleted(files_in_outputs_bucket: list[str]) -> bool:
    """
    Checks to see if all of the input and output files have been deleted from their respective buckets
    :return: True if they have been deleted, False otherwise.
    """
    deleted_outputs = are_deleted(files_in_outputs_bucket)
    if not deleted_outputs:
        return False

    deleted_inputs = are_deleted(files_in_outputs_bucket)
    if not deleted_inputs:
        return False

    return True


def are_deleted(files: list) -> bool:
    """
    Have these files been deleted from the bucket

    :files: A dictionary of filenames to check. The filename must include the bucket and path.
    :return: True if they have been deleted, False otherwise.
    """
    for filename in files:
        full_filename = f"{OUTPUT_BUCKET_NAME}/{filename}"
        bucket = full_filename.split('/', 1)[0]
        file_path = full_filename.split('/', 1)[1]
        exists = check_file_exists(file_path, bucket)
        if exists:
            return False
        else:
            print(f"{full_filename} has been deleted")

    return True


def is_datastore_cleaned_up() -> bool:
    for fake_id in fake_surveys:
        length = get_entity_count(fake_id + '_201605')
        return length < 1


def list_blobs() -> list[str]:
    """Lists all the blobs in the bucket."""
    file_list = []

    storage_client = storage.Client()

    blobs = storage_client.list_blobs(f'{PROJECT_ID}-outputs')

    # Note: The call returns a response only when the iterator is consumed.
    for blob in blobs:
        file_list.append(blob.name)
    return file_list


def wait_for_outputs_and_return_list_of_them(expected_num_of_files: int) -> list[str]:
    file_list = list_blobs()
    t = 0
    while len(file_list) < expected_num_of_files:
        print("-" * 50)
        print(f"Waiting for outputs, waited {t} seconds...")
        time.sleep(1)
        t += 1
        print("-" * 50)
        file_list = list_blobs()
        if t >= MAX_TIMEOUT_IN_SECONDS:
            raise TimeoutError("Timed out getting outputs")
    print(f"Successfully retrieved outputs: {file_list}")
    return file_list
