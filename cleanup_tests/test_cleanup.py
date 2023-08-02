import unittest
import time
from cleanup_tests.helper_functions import setup_output_and_input_buckets, setup_comments, kickoff_cleanup_outputs, \
    have_files_been_deleted, is_datastore_cleaned_up

TIMEOUT = 150


class TestCleanup(unittest.TestCase):
    """
    The functions called within setUpClass need to be run to 'setup' the tests. They can be found in helper_functions.py
    """

    @classmethod
    def setUpClass(cls):
        setup_output_and_input_buckets()
        setup_comments()

    def test_outputs_and_inputs_buckets(self):
        t = 0

        print("-" * 50)
        while t < 60:
            print(f"Slept for {t} seconds...")
            time.sleep(1)
            t += 1
        print("-" * 50)

        kickoff_cleanup_outputs()
        count = 0
        passed = False
        while count < TIMEOUT:
            if have_files_been_deleted():
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
