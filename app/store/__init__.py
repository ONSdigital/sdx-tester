from google.cloud import storage
from app import PROJECT_ID

OUTPUT_BUCKET_NAME = f'{PROJECT_ID}-outputs'
INPUT_SEFT_BUCKET = f'{PROJECT_ID}-sefts'

storage_client = storage.Client(PROJECT_ID)
