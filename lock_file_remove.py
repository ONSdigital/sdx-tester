from app.store.writer import remove_from_bucket
from google.api_core.exceptions import NotFound

BUCKET_NAME = "sdx-tester-lock"
FILE_NAME = 'lock.txt'


def remove_lock_file():
    try:
        remove_from_bucket(FILE_NAME, BUCKET_NAME)
    except NotFound as err:
        print(f'File does not exist: {err}')
        raise NotFound
