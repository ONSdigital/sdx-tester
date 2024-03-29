import structlog
from app.store import INPUT_SEFT_BUCKET, storage_client

logger = structlog.get_logger()


def write_seft(data, filename: str):
    logger.info("Writing SEFT to Storage Bucket")
    write(data, filename, INPUT_SEFT_BUCKET)


def write(data: str, filename: str, bucket: str) -> None:
    """
    Will write data to a bucket and return the filename of
    the new data

    """
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(filename)
    blob.upload_from_string(data)


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
