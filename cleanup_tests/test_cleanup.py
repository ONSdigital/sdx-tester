import unittest

from datetime import date, datetime
from google.cloud import storage
from cleanup_tests import test_data, ignore_warnings
from comment_tests.test_setup import datastore_client


class TestCleanup(unittest.TestCase):
    """
    Please ensure you have run test_setup.py within this package before running these tests
    """

    @ignore_warnings
    def test_outputs_bucket(self):
        for data, filename in test_data.items():
            bucket = filename.split('/', 1)[0]
            file_path = filename.split('/', 1)[1]
            self.assertFalse(bucket_check_if_exists(file_path, bucket))

    @ignore_warnings
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
