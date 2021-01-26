import logging
import os

import gnupg
from flask import Flask
from flask_socketio import SocketIO

LOGGING_LEVEL = logging.getLevelName(os.getenv('LOGGING_LEVEL', 'INFO'))
LOGGING_FORMAT = "%(asctime)s.%(msecs)06dZ|%(levelname)s: sdx-tester: thread: %(thread)d %(message)s"

logging.basicConfig(
    format=LOGGING_FORMAT,
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=LOGGING_LEVEL,
)

PROJECT_ID = os.getenv('PROJECT_ID', 'ons-sdx-tom')
BUCKET_NAME = f'{PROJECT_ID}-outputs'

# publishing config
SURVEY_TOPIC = "survey-topic"

# Subscriber config
DAP_SUBSCRIPTION = "dap-subscription"

QUARANTINE_SUBSCRIPTION = "quarantine-subscription"

RECEIPT_SUBSCRIPTION = "receipt-subscription"

MAX_WAIT_TIME_SECS = 30

gpg = gnupg.GPG()

with open('dap_private_key.asc') as f:
    key_data = f.read()
import_result = gpg.import_keys(key_data)


app = Flask(__name__)
socketio = SocketIO(app)

from app import routes
