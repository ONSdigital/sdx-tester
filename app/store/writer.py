import logging

from google.cloud import storage
from app.store import SEFT_BUCKET, PROJECT_ID
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def write_seft(data, filename: str):
    logger.info("Writing SEFT to Storage Bucket")
    write(data, filename, SEFT_BUCKET)


def write(data: str, filename: str, bucket: str) -> str:
    path = filename
    storage_client = storage.Client(PROJECT_ID)
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(path)
    blob.upload_from_string(data)
    return path
