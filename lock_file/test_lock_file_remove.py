import unittest
from app.store.writer import remove_from_bucket
from lock_file import FILE_NAME, BUCKET_NAME
from google.api_core.exceptions import NotFound


class TestCleanupSetup(unittest.TestCase):

    def test_remove_lock_file(self):
        try:
            remove_from_bucket(FILE_NAME, BUCKET_NAME)
        except NotFound as err:
            print(f'File does not exist: {err}')
            raise NotFound
