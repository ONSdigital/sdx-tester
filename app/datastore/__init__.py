"""
File containing variables
and methods for managing datastore
"""

from google.cloud import datastore
from app import PROJECT_ID

DATASTORE_NAMESPACE = "toolbox"
QUARANTINE_KIND = "quarantined_messages"
DATASTORE_CLIENT = datastore.Client(project=PROJECT_ID, namespace=DATASTORE_NAMESPACE)
