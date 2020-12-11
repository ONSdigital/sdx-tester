import json
from google.cloud import storage


def read(filename: str) -> str:
    path = f"surveys/{filename}"
    # create storage client
    storage_client = storage.Client("ons-sdx-sandbox")
    # get bucket with name
    bucket = storage_client.bucket('sdx-outputs')
    # get bucket data as blob
    blob = bucket.blob('sdx-output')
    # convert to string
    json_data = blob.download_as_string()
    return json_data


def get_filename(json_str):
    message_dict = json.loads(json_str)
    message_name = message_dict['files'][0]["name"]
    return message_name