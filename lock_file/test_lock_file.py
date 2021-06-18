import json
import os
import time
import unittest

from app.store.reader import check_bucket_exists, check_file_exists
from app.store.writer import create_bucket_class_location, write
from lock_file import BUCKET_NAME, FILE_NAME

service = os.getenv('SERVICE', 'No Service Provided')
version = os.getenv('VERSION', 'No version Provided')
TIMEOUT = 10000


class LockFile(unittest.TestCase):

    finished_locking = False
    count = 0
    lock_file_data = json.dumps({
        'SERVICE': service,
        'VERSION': version
    })

    def test_lock_file(self):

        print('checking if bucket exists')
        if not check_bucket_exists(BUCKET_NAME):
            print('No Bucket, creating one')
            create_bucket_class_location(BUCKET_NAME)
            print('successfully created')

        print('checking if lock_file present')
        if not check_file_exists(FILE_NAME, BUCKET_NAME):

            print(f'lock_file not present, writing lock file: {self.lock_file_data}')
            write(self.lock_file_data, FILE_NAME, BUCKET_NAME)
            self.finished_locking = True

        else:
            while check_file_exists(FILE_NAME, BUCKET_NAME):
                print(f'waiting another 30 seconds, {self.count} seconds so far')
                time.sleep(30)
                self.count += 30
            print(f'lock_file not present after {self.count} seconds, writing lock file: {self.lock_file_data}')
            write(self.lock_file_data, FILE_NAME, BUCKET_NAME)
            self.finished_locking = True

        self.assertTrue(self.finished_locking)
