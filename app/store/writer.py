import logging

from app.store import INPUT_SEFT_BUCKET, storage_client
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def write_seft(data, filename: str):
    logger.info("Writing SEFT to Storage Bucket")
    write(data, filename, INPUT_SEFT_BUCKET)


def write(data: str, filename: str, bucket: str) -> str:
    path = filename
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(path)
    blob.upload_from_string(data)
    return path
