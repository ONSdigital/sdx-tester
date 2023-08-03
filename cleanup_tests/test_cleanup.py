import unittest
import time

from app import PROJECT_ID
from app.store.bucket_cleanup import delete_files_in_bucket
from cleanup_tests import EXPECTED_NUM_OF_OUTPUT_FILES
from cleanup_tests.helper_functions import setup_input_and_output_buckets, setup_comments, kickoff_cleanup_outputs, \
    have_files_been_deleted, is_datastore_cleaned_up, wait_for_outputs_and_return_list_of_them

TIMEOUT = 60


class TestCleanup(unittest.TestCase):
    """
    The functions called within setUpClass need to be run to 'setup' the tests. They can be found in helper_functions.py
    """

    @classmethod
    def setUpClass(cls):
        delete_files_in_bucket(f'{PROJECT_ID}-outputs')
        delete_files_in_bucket(f'{PROJECT_ID}-survey-responses')
        setup_input_and_output_buckets()
        setup_comments()
        cls.files_in_outputs_bucket = wait_for_outputs_and_return_list_of_them(EXPECTED_NUM_OF_OUTPUT_FILES)
        kickoff_cleanup_outputs(cls.files_in_outputs_bucket)

    def test_outputs_and_inputs_buckets(self):
        count = 0
        passed = False
        while count < TIMEOUT:
            if have_files_been_deleted(self.files_in_outputs_bucket):
                print('All files have been deleted')
                passed = True
                break
            else:
                print('The files have not yet been deleted. Waiting 10 seconds...')
                time.sleep(10)
                count += 10
        self.assertTrue(passed)

    def test_comments_datastore(self):
        count = 0
        passed = False
        while count < TIMEOUT:
            if is_datastore_cleaned_up():
                print('The comments have been deleted')
                passed = True
                break
            else:
                print('The comments are not deleted yet. Waiting 10 seconds...')
                time.sleep(10)
                count += 10
        self.assertTrue(passed)




