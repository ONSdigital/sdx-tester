from google.cloud import storage
from app import PROJECT_ID

OUTPUT_BUCKET_NAME = f'{PROJECT_ID}-outputs'
INPUT_SEFT_BUCKET = f'{PROJECT_ID}-seft-responses'
INPUT_SURVEY_BUCKET = f'{PROJECT_ID}-survey-responses'

storage_client = storage.Client(PROJECT_ID)
