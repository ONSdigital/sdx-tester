import unittest

from app.store.reader import check_file_exists, datastore_check_if_exists
from cleanup_tests import test_data, fake_surveys


class TestCleanup(unittest.TestCase):
    """
    Please ensure you have run helper_functions.py within this package before running these tests
    """

    def test_outputs_bucket(self):
        for data, filename in test_data.items():
            bucket = filename.split('/', 1)[0]
            file_path = filename.split('/', 1)[1]
            self.assertFalse(check_file_exists(file_path, bucket))

    def test_comments_datastore(self):
        for fake_id in fake_surveys:
            length = datastore_check_if_exists(fake_id + '_201605')
            self.assertEquals(length, 0)
