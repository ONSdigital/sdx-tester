import logging

from app.store import INPUT_SEFT_BUCKET, storage_client
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def write_seft(data, filename: str):
    logger.info("Writing SEFT to Storage Bucket")
    write(data, filename, INPUT_SEFT_BUCKET)


def write(data: str, filename: str, bucket: str) -> str:
    """
    Uploads a string submission to the GCP output bucket: {PROJECT_ID}-outputs or input seft bucket {PROJECT_ID}-seft-responses
    """
    path = filename
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(path)
    blob.upload_from_string(data)
    return path


def create_bucket_class_location(bucket_name):
    """Create a new bucket in specific location with storage class"""
    # bucket_name = "your-new-bucket-name"
    bucket = storage_client.bucket(bucket_name)
    bucket.storage_class = "STANDARD"
    new_bucket = storage_client.create_bucket(bucket, location="europe-west2")

    print(
        "Created bucket {} in {} with storage class {}".format(
            new_bucket.name, new_bucket.location, new_bucket.storage_class
        )
    )
    return new_bucket


def remove_from_bucket(folder_and_file, bucket_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(folder_and_file)
    blob.delete()
    logger.info(f"Successfully deleted: {folder_and_file} from {bucket_name}.")
