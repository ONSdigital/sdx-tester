import unittest

from app.store.reader import check_file_exists, datastore_check_if_exists
from cleanup_tests import test_data, ignore_warnings


class TestCleanup(unittest.TestCase):
    """
    Please ensure you have run test_setup.py within this package before running these tests
    """

    @ignore_warnings
    def test_outputs_bucket(self):
        for data, filename in test_data.items():
            bucket = filename.split('/', 1)[0]
            file_path = filename.split('/', 1)[1]
            self.assertFalse(check_file_exists(file_path, bucket))

    @ignore_warnings
    def test_comments_datastore(self):
        length = datastore_check_if_exists()
        self.assertEquals(length, 0)
