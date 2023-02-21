import io
import zipfile
import structlog

from google.api_core.exceptions import NotFound
from google.cloud import storage
from app.store import OUTPUT_BUCKET_NAME, storage_client
from app.gpg.decryption import decrypt_output

logger = structlog.get_logger()


def get_files(file_path) -> dict:
    """
    For survey submissions, intended for the legacy system, SDX transforms them into several different files
    which are zipped up together and then encrypted.

    Comments are extracted from the survey submissions and batched up into xlsx files and zipped up every morning.
    The output is encrypted zip files.

    This function reads those encrypted zip, decrypts the output and extracts the zip for survey submissions and
    significant comments. Extraction is not required for other types of submissions.
    """
    file_dir = file_path.split("/")[0]
    filename = file_path.split("/")[1]
    if file_dir == 'survey' or file_dir == 'comments':
        encrypted_zip = read(file_path, OUTPUT_BUCKET_NAME)
        zip_bytes = decrypt_output(encrypted_zip, filename)
        return extract_zip(zip_bytes)
    else:
        encrypted_data = read(file_path, OUTPUT_BUCKET_NAME)
        data_bytes = decrypt_output(encrypted_data, filename)
        if file_dir == 'seft':
            files = {'SEFT': data_bytes}
        else:
            files = {'JSON': data_bytes.decode()}
        return files


def read(file_path, bucket) -> bytes:
    """Retrieve a file from GCP output bucket: {PROJECT_ID}-outputs"""
    try:
        # get bucket with name
        bucket = storage_client.bucket(bucket)
        # get bucket data as blob
        blob = bucket.blob(file_path)
        # convert to bytes
        file = blob.download_as_bytes()
        return file

    except NotFound as e:
        print(e)


def extract_zip(zip_bytes: bytes) -> dict:
    z = zipfile.ZipFile(io.BytesIO(zip_bytes), "r")
    files = {}
    for filename in z.namelist():
        logger.info(f'File: {filename}')
        file_bytes = z.read(filename)
        files[filename] = file_bytes

    z.close()
    return files


def get_comment_files() -> bytes:
    bucket = storage_client.bucket(OUTPUT_BUCKET_NAME)
    files = bucket.list_blobs(prefix='comments')
    file_list = [(file.name, file.time_created) for file in files]
    print(file_list)
    file_list = sorted(file_list, key=lambda f: f[1], reverse=True)
    print(file_list)
    latest_filename = file_list[0][0]
    encrypted_zip = read(latest_filename, OUTPUT_BUCKET_NAME)
    zip_bytes = decrypt_output(encrypted_zip, 'comments')
    return zip_bytes


def does_comment_exist() -> bool:
    bucket = storage_client.bucket(OUTPUT_BUCKET_NAME)
    files = bucket.list_blobs(prefix='comments')
    file_list = [file.name for file in files]
    return len(file_list) > 0


def check_file_exists(file_name, bucket=OUTPUT_BUCKET_NAME) -> bool:
    logger.info(f'Checking for: {file_name} in {bucket}')
    bucket = storage_client.bucket(bucket)
    return storage.Blob(bucket=bucket, name=file_name).exists(storage_client)


def check_bucket_exists(my_bucket) -> bool:
    list_of_buckets = storage_client.list_buckets()
    for x in list_of_buckets:
        if my_bucket == x.name:
            return True
    return False
