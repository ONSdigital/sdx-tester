import base64
import io
import json
import zipfile

from google.cloud import storage
from app import BUCKET_NAME, PROJECT_ID
from app.encryption import decrypt_survey, view_zip_content


def get_files(file_path) -> list:
    if file_path.split("/")[0] != 'dap':
        encrypted_zip = read(file_path)
        encoded_zip = decrypt_survey(encrypted_zip)
        decoded = base64.b64decode(encoded_zip['zip'])
        return extract_zip(decoded)
        # return extract_zip(decoded)
    else:
        e_json = read(file_path)
        d_json = decrypt_survey(e_json)
        files = {'JSON': d_json}
        return files


def read(file_path) -> str:
    # create storage client
    storage_client = storage.Client(PROJECT_ID)
    # get bucket with name
    bucket = storage_client.bucket(BUCKET_NAME)
    # get bucket data as blob
    blob = bucket.blob(file_path)
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
