import time
from datetime import datetime

from app.store_reader import read


def check_bucket_for_comments():
    time.sleep(10)
    date_time = datetime.utcnow()
    file_name = f"{date_time.strftime('%Y-%m-%d')}.zip"
    comments = read(file_name, 'comments')
    if comments:
        return True
    else:
        return False
