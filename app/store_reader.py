import io
import json
import zipfile

from google.cloud import storage
from app import BUCKET_NAME, PROJECT_ID

DAP_SURVEYS = ["023", "134", "147", "281", "283", "lms", "census"]


def get_files(file_name: str, file_location) -> list:
    if file_location not in DAP_SURVEYS:
        zip_file = read(file_name, 'surveys')
        return extract_zip(zip_file)
    else:
        b_str_data = read(file_name, 'dap')
        files = {'JSON': b_str_data}
        return files


def read(file_name: str, file_location) -> str:
    path = f"{file_location}/{file_name}"
    # create storage client
    storage_client = storage.Client(PROJECT_ID)
    # get bucket with name
    bucket = storage_client.bucket(BUCKET_NAME)
    # get bucket data as blob
    blob = bucket.blob(path)
    # convert to bytes
    json_data = blob.download_as_bytes()

    return json_data


def extract_zip(zip_file: str) -> dict:
    z = zipfile.ZipFile(io.BytesIO(zip_file), "r")
    files = {}
    for filename in z.namelist():
        print(f'File: {filename}')
        file_bytes = z.read(filename)
        files[filename] = file_bytes

    z.close()
    return files


def get_filename(json_str):
    message_dict = json.loads(json_str)
    message_name = message_dict['files'][0]['name']
    return message_name[:-5]
