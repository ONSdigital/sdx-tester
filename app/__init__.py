import logging
import os


from flask import Flask
from flask_socketio import SocketIO

LOGGING_LEVEL = logging.getLevelName(os.getenv('LOGGING_LEVEL', 'INFO'))
LOGGING_FORMAT = "%(asctime)s.%(msecs)06dZ|%(levelname)s: sdx-tester: %(message)s"

logging.basicConfig(
    format=LOGGING_FORMAT,
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=LOGGING_LEVEL,
)

PROJECT_ID = "ons-sdx-sandbox"

# publishing config
SURVEY_TOPIC = "survey-topic"

# Subscriber config
DAP_SUBSCRIPTION = "dap-subscription"

QUARANTINE_SUBSCRIPTION = "quarantine-subscription"

RECEIPT_SUBSCRIPTION = "receipt-subscription"

MAX_WAIT_TIME_SECS = 20


app = Flask(__name__)
socketio = SocketIO(app)

from app import routes
