import logging
import os

from flask import Flask
from flask_socketio import SocketIO

LOGGING_LEVEL = logging.getLevelName(os.getenv('LOGGING_LEVEL', 'INFO'))
LOGGING_FORMAT = "%(asctime)s.%(msecs)06dZ|%(levelname)s: sdx-tester: thread: %(thread)d %(message)s"

logging.basicConfig(
    format=LOGGING_FORMAT,
    datefmt="%Y-%m-%dT%H:%M:%S",
    level='INFO',
)

PROJECT_ID = os.getenv('PROJECT_ID', 'ons-sdx-sandbox')

app = Flask(__name__)
socketio = SocketIO(app)

from app.ui import routes
from app.messaging import message_manager


def start():
    message_manager.start()
