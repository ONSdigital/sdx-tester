import unittest
from datetime import date, datetime

from google.cloud import storage

from app.store import OUTPUT_BUCKET_NAME, INPUT_SEFT_BUCKET
from cleanup_tests.test_setup import comment_filename
from comment_tests.test_setup import datastore_client


class TestCleanup(unittest.TestCase):
    test_data = {
        'Silly Survey Data': f'{OUTPUT_BUCKET_NAME}/survey/testing_cleanup_function-survey',
        'Silly SEFT Data': f'{OUTPUT_BUCKET_NAME}/seft/testing_cleanup_function-seft',
        'Silly dap Data': f'{OUTPUT_BUCKET_NAME}/dap/testing_cleanup_function-dap',
        'Silly legacy Data': f'{OUTPUT_BUCKET_NAME}/legacy/testing_cleanup_function-legacy',
        'Silly seft-input Data': f'{INPUT_SEFT_BUCKET}/seft/testing_cleanup_function-seft',
        'Silly comment Data': f'{OUTPUT_BUCKET_NAME}/comments/{comment_filename()}.zip'
    }

    def test_outputs_bucket(self):
        for data, filename in self.test_data.items():
            bucket = filename.split('/', 1)[0]
            file_path = filename.split('/', 1)[1]
            self.assertFalse(bucket_check_if_exists(file_path, bucket))

    def test_comments_datastore(self):
        length = datastore_check_if_exists()
        self.assertEquals(length, 0)


def bucket_check_if_exists(file_name, bucket):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket)
    return storage.Blob(bucket=bucket, name=file_name).exists(storage_client)


def datastore_check_if_exists():
    d = date.today()
    today = datetime(d.year, d.month, d.day)
    query = datastore_client.query(kind='Comment')
    query.add_filter("created", "<", today)
    return len(list(query.fetch()))
