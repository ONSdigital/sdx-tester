import structlog

from app import PROJECT_ID
from app.store.writer import remove_from_bucket
from google.api_core.exceptions import NotFound
logger = structlog.get_logger()

BUCKET_NAME = f"{PROJECT_ID}-lock-file"
FILE_NAME = 'lock.txt'


def remove_lock_file():
    try:
        remove_from_bucket(FILE_NAME, BUCKET_NAME)
    except NotFound as err:
        logger.error(f'File does not exist: {err}')
        raise NotFound


if __name__ == '__main__':
    remove_lock_file()
