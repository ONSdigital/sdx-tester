import os
from flask import Flask
from flask_socketio import SocketIO

from app.config import Config


PROJECT_ID = os.getenv('PROJECT_ID')

# Create a config object to store settings etc
CONFIG = Config(PROJECT_ID)

listen = 'TRUE' != os.getenv('DISABLE_LISTENING', 'FALSE') # Allow tester to be run without listening
DATA_RECIPIENT = os.getenv('DATA_RECIPIENT', 'dap@ons.gov.uk')

app = Flask(__name__)
socketio = SocketIO(app)


# Configure Flask app settings
app.secret_key = os.urandom(12).hex()
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True


from app.datastore import DATASTORE_TOOLBOX_CLIENT, DATASTORE_TOOLBOX_NAMESPACE
from app.messaging import get_message_manager
message_manager = get_message_manager(listen)
from app import routes


def start():
    message_manager.start()
