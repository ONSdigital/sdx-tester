from google.api_core.exceptions import NotFound
from datetime import datetime

from app.store_reader import read, extract_zip


def check_bucket_for_comments():
    date_time = datetime.utcnow()
    file_name = f"{date_time.strftime('%Y-%m-%d')}.zi"
    try:
        extract_zip(read(file_name, 'comments'))
    except NotFound as err:
        print(err)
        return err


if __name__ == '__main__':
    check_bucket_for_comments()
