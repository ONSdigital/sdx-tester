import os

from flask import Flask
from flask_socketio import SocketIO

PROJECT_ID = os.getenv('PROJECT_ID')
listen = 'TRUE' != os.getenv('DISABLE_LISTENING', 'FALSE') # Allow tester to be run without listening
DATA_RECIPIENT = os.getenv('DATA_RECIPIENT', 'dap@ons.gov.uk')

app = Flask(__name__)
socketio = SocketIO(app)

from app.datastore import DATASTORE_TOOLBOX_CLIENT, DATASTORE_TOOLBOX_NAMESPACE
from app.messaging import get_message_manager
message_manager = get_message_manager(listen)

from app import routes


def start():
    message_manager.start()
