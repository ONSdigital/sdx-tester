import json
from concurrent.futures import TimeoutError
from app import survey_subscriber, subscription_path
from google.cloud import storage


def callback(message):
    filename = get_filename(message.data)
    print(read(filename))
    message.ack()


def start():
    streaming_pull_future = survey_subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with survey_subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result()
        except TimeoutError:
            streaming_pull_future.cancel()


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
