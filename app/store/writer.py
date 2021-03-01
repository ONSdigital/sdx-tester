from google.cloud import storage
from app.store import SEFT_BUCKET, PROJECT_ID


def write_seft(data, filename: str):
    print(f'This is the filename in write_seft method {filename}')
    print("writing seft to bucket")
    write(data, filename, SEFT_BUCKET)


def write(data: str, filename: str, bucket: str, directory: str = '') -> str:
    path = f"{directory}/{filename}"
    print(f' This is the seft bucket path in write method of writer.py {path}')
    storage_client = storage.Client(PROJECT_ID)
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(path)
    blob.upload_from_string(data)
    return path
