import logging
import os
import gnupg

from google.cloud import storage
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

class Config:
    def __init__(self, proj_id):
        self.PROJECT_ID = proj_id
        self.BUCKET_NAME = f'{proj_id}-outputs'
        self.SEFT_BUCKET_NAME = f'{proj_id}-sefts'
        self.BUCKET = None
        self.SEFT_BUCKET = None
        self.SURVEY_TOPIC_PATH = None
        self.SEFT_TOPIC_PATH = None
        self.DAP_SUBSCRIPTION = None
        self.QUARANTINE_SUBSCRIPTION = None
        self.SEFT_QUARANTINE_SUBSCRIPTION = None
        self.RECEIPT_SUBSCRIPTION = None
        self.GPG = None
        self.ENCRYPTION_KEY = None
        self.KEY_PURPOSE_SUBMISSION = None

CONFIG = Config(project_id)

def cloud_config():
    print('loading cloud config')
    CONFIG.DAP_SUBSCRIPTION = "dap-subscription"
    gpg = gnupg.GPG()
    with open('dap_private_key.asc') as f:
        key_data = f.read()
        f.close()
    gpg.import_keys(key_data)
    CONFIG.ENCRYPTION_KEY = key_data
    CONFIG.GPG = gpg
    storage_client = storage.Client(CONFIG.PROJECT_ID)
    CONFIG.BUCKET = storage_client(CONFIG.BUCKET_NAME)
    CONFIG.SEFT_BUCKET = storage_client(CONFIG.SEFT_BUCKET_NAME)


app = Flask(__name__)
socketio = SocketIO(app)

from app.ui import routes
from app.messaging import message_manager


def start():
    message_manager.start()
