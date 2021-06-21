import json
import os
import time
import structlog

from app import PROJECT_ID
from app.store.reader import check_bucket_exists, check_file_exists
from app.store.writer import create_bucket_class_location, write

logger = structlog.get_logger()

service = os.getenv('SERVICE', 'No Service Provided')
version = os.getenv('VERSION', 'No version Provided')

BUCKET_NAME = f"{PROJECT_ID}-lock-file"
FILE_NAME = 'lock.txt'
lock_file_data = json.dumps({
    'SERVICE': service,
    'VERSION': version
})


def lock_file():
    count = 0
    logger.info(f'Checking if bucket exists: {BUCKET_NAME}')
    if not check_bucket_exists(BUCKET_NAME):
        logger.info('No Bucket, creating one')
        create_bucket_class_location(BUCKET_NAME)

    logger.info(f'Checking if {FILE_NAME} present in {BUCKET_NAME}')
    if not check_file_exists(FILE_NAME, BUCKET_NAME):

        logger.info(f'{FILE_NAME} not present, writing lock file: {lock_file_data}')
        write(lock_file_data, FILE_NAME, BUCKET_NAME)
        return True

    else:
        while check_file_exists(FILE_NAME, BUCKET_NAME):
            logger.info(f'Waiting 30 seconds, {count} seconds so far')
            time.sleep(30)
            count += 30
        logger.info(f'{FILE_NAME} not present after {count} seconds, writing lock file: {lock_file_data}')
        write(lock_file_data, FILE_NAME, BUCKET_NAME)
        return True


if __name__ == '__main__':
    lock_file()
