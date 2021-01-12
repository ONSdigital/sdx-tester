import io
import json
import zipfile

from google.cloud import storage
from app import BUCKET_NAME, PROJECT_ID


def get_files(filename: str) -> list:
    data_str = read(filename)
    # decrypt
    return extract(data_str)


def read(filename: str) -> str:
    path = f"surveys/{filename}"
    # create storage client
    storage_client = storage.Client(PROJECT_ID)
    # get bucket with name
    bucket = storage_client.bucket(BUCKET_NAME)
    # get bucket data as blob
    blob = bucket.blob(path)
    # convert to string
    json_data = blob.download_as_string()
    return json_data


def extract(zip_file: str) -> dict:
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
    message_name = message_dict['files'][0]["name"]
    return message_name[:-5]
