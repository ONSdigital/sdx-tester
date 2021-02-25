import logging
import os
import gnupg

from google.cloud import storage, pubsub_v1, datastore
from flask import Flask
from flask_socketio import SocketIO

LOGGING_LEVEL = logging.getLevelName(os.getenv('LOGGING_LEVEL', 'INFO'))
LOGGING_FORMAT = "%(asctime)s.%(msecs)06dZ|%(levelname)s: sdx-tester: thread: %(thread)d %(message)s"

logging.basicConfig(
    format=LOGGING_FORMAT,
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=LOGGING_LEVEL,
)

project_id = os.getenv('PROJECT_ID', 'ons-sdx-sandbox')

gpg = gnupg.GPG()
with open('dap_private_key.asc') as f:
    key_data = f.read()
    f.close()
gpg.import_keys(key_data)


class Config:
    def __init__(self, proj_id) -> None:
        self.PROJECT_ID = proj_id
        self.BUCKET_NAME = f'{proj_id}-outputs'
        self.SEFT_BUCKET_NAME = f'{proj_id}-sefts'
        self.KEY_PURPOSE_SUBMISSION = 'submission'
        self.DAP_SUBSCRIPTION = 'dap-subscription'
        self.DAP_RECIPIENT = 'dap@ons.gov.uk'
        self.QUARANTINE_SUBSCRIPTION = 'quarantine-subscription'
        self.SEFT_QUARANTINE_SUBSCRIPTION = 'quarantine-seft-subscription'
        self.RECEIPT_SUBSCRIPTION = 'receipt-subscription'
        self.DATASTORE_CLIENT = None
        self.PUBLISHER = None
        self.SUBSCRIBER = None
        self.SURVEY_TOPIC_PATH = None
        self.SEFT_TOPIC_PATH = None
        self.MAX_WAIT_TIME_SECS = 30
        self.BUCKET = None
        self.SEFT_BUCKET = None
        self.ENCRYPTION_KEY = key_data
        self.GPG = gpg


CONFIG = Config(project_id)


def cloud_config():
    print('loading cloud config')
    publisher = pubsub_v1.PublisherClient()
    CONFIG.SURVEY_TOPIC_PATH = publisher.topic_path(CONFIG.PROJECT_ID, 'survey-topic')
    CONFIG.SEFT_TOPIC_PATH = publisher.topic_path(CONFIG.PROJECT_ID, 'seft-topic')
    CONFIG.PUBLISHER = publisher
    CONFIG.SUBSCRIBER = pubsub_v1.SubscriberClient()
    CONFIG.DATASTORE_CLIENT = datastore.Client(project=CONFIG.PROJECT_ID)
    storage_client = storage.Client(CONFIG.PROJECT_ID)
    CONFIG.BUCKET = storage_client.bucket(CONFIG.BUCKET_NAME)
    CONFIG.SEFT_BUCKET = storage_client.bucket(CONFIG.SEFT_BUCKET_NAME)


app = Flask(__name__)
socketio = SocketIO(app)

from app.ui import routes
from app.messaging.manager import MessageManager
message_manager = MessageManager()


def start():
    message_manager.start()
