from app.store import INPUT_SEFT_BUCKET, storage_client


def write_seft(data, filename: str):
    print("writing seft to bucket")
    write(data, filename, INPUT_SEFT_BUCKET)


def write(data: str, filename: str, bucket: str) -> str:
    path = filename
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(path)
    blob.upload_from_string(data)
    return path
