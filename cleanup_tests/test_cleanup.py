import unittest
import time

from datetime import time
from app.store.reader import check_file_exists, get_entity_count
from cleanup_tests import test_data, fake_surveys
from cleanup_tests.helper_functions import setup_output_bucket, setup_comments, kickoff_cleanup_outputs, \
    is_bucket_empty, is_datastore_cleaned_up

TIMEOUT = 150


class TestCleanup(unittest.TestCase):
    """
    Please ensure you have run helper_functions.py within this package before running these tests
    """

    @classmethod
    def setUpClass(cls):
        setup_output_bucket()
        setup_comments()
        kickoff_cleanup_outputs()

    def test_outputs_bucket(self):
        count = 0
        passed = False
        while count < TIMEOUT:
            if is_bucket_empty():
                passed = True
                break
            else:
                print('The bucket is not empty yet. Waiting 20 seconds...')
                time.sleep(20)
                count += 20
        self.assertTrue(passed)

    def test_comments_datastore(self):
        count = 0
        passed = False
        while count < TIMEOUT:
            if is_datastore_cleaned_up():
                passed = True
                break
            else:
                print(' The comments are not deleted yet. Waiting 20 seconds...')
                time.sleep(20)
                count += 20
            self.assertTrue(passed)
