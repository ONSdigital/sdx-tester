import logging
import os

from flask import Flask
from flask_socketio import SocketIO

LOGGING_LEVEL = logging.getLevelName(os.getenv('LOGGING_LEVEL', 'INFO'))
LOGGING_FORMAT = "%(asctime)s.%(msecs)06dZ|%(levelname)s: sdx-tester: thread: %(thread)d %(message)s"

logging.basicConfig(
    format=LOGGING_FORMAT,
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=LOGGING_LEVEL,
)

PROJECT_ID = os.getenv('PROJECT_ID', 'ons-sdx-sandbox')
# Allow tester to be run without listening
listen = 'TRUE' != os.getenv('DISABLE_LISTENING', 'FALSE')

app = Flask(__name__)
socketio = SocketIO(app)

from app.messaging import get_message_manager
message_manager = get_message_manager(listen)

from app.ui import routes


def start():
    message_manager.start()
