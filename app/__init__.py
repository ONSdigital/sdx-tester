import os

from flask import Flask
from flask_socketio import SocketIO
from app.logger import logging_config

logging_config()

PROJECT_ID = os.getenv('PROJECT_ID')
# Allow tester to be run without listening
listen = 'TRUE' != os.getenv('DISABLE_LISTENING', 'FALSE')

DATA_RECIPIENT = os.getenv('DATA_RECIPIENT', 'dap@ons.gov.uk')

app = Flask(__name__)
socketio = SocketIO(app)

from app.messaging import get_message_manager
message_manager = get_message_manager(listen)

from app.ui import routes


def start():
    message_manager.start()
