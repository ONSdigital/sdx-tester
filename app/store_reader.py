import io
import json
import zipfile

from google.cloud import storage
from app import BUCKET_NAME, PROJECT_ID
from app.decryption import decrypt_output


def get_files(file_path) -> dict:
    dir = file_path.split("/")[0]
    filename = file_path.split("/")[1]
    if dir == 'survey' or dir == 'comments':
        encrypted_zip = read(file_path)
        zip_bytes = decrypt_output(encrypted_zip, filename)
        return extract_zip(zip_bytes)
    else:
        encrypted_data = read(file_path)
        data_bytes = decrypt_output(encrypted_data, filename)
        files = {'JSON': data_bytes.decode()}
        return files


def read(file_path) -> bytes:
    # create storage client
    storage_client = storage.Client(PROJECT_ID)
    # get bucket with name
    bucket = storage_client.bucket(BUCKET_NAME)
    # get bucket data as blob
    blob = bucket.blob(file_path)
    # convert to bytes
    json_data = blob.download_as_bytes()

    return json_data


def extract_zip(zip_bytes: bytes) -> dict:
    z = zipfile.ZipFile(io.BytesIO(zip_bytes), "r")
    files = {}
    for filename in z.namelist():
        print(f'File: {filename}')
        file_bytes = z.read(filename)
        files[filename] = file_bytes

    z.close()
    return files


def get_filename(json_str):
    message_dict = json.loads(json_str)
    message_name = message_dict['temp_files'][0]['name']
    return message_name[:-5]
