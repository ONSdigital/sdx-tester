import json
import os
import time

from app.store.reader import check_bucket_exists, check_file_exists
from app.store.writer import create_bucket_class_location, write

BUCKET_NAME = "sdx-tester-lock"
FILE_NAME = 'lock.txt'
service = os.getenv('SERVICE', 'No Service Provided')
version = os.getenv('VERSION', 'No version Provided')
TIMEOUT = 10000

lock_file_data = json.dumps({
    'SERVICE': service,
    'VERSION': version
})


def lock_file():
    count = 0
    print('checking if bucket exists')
    if not check_bucket_exists(BUCKET_NAME):
        print('No Bucket, creating one')
        create_bucket_class_location(BUCKET_NAME)
        print('successfully created')

    print('checking if lock_file_scripts present')
    if not check_file_exists(FILE_NAME, BUCKET_NAME):

        print(f'lock_file_scripts not present, writing lock file: {lock_file_data}')
        write(lock_file_data, FILE_NAME, BUCKET_NAME)
        return True

    else:
        while check_file_exists(FILE_NAME, BUCKET_NAME):
            print(f'waiting another 30 seconds, {count} seconds so far')
            time.sleep(30)
            count += 30
        print(f'lock_file_scripts not present after {count} seconds, writing lock file: {lock_file_data}')
        write(lock_file_data, FILE_NAME, BUCKET_NAME)
        return True


if __name__ == '__main__':
    lock_file()
