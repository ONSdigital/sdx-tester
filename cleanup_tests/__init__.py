from datetime import datetime
from app.store import OUTPUT_BUCKET_NAME, INPUT_SEFT_BUCKET, INPUT_SURVEY_BUCKET
from app.survey_loader import SurveyLoader

SEFT_DIR = "app/Data/v1/seft"


def comment_filename():
    date_time = datetime.utcnow()
    return date_time.strftime('%Y-%m-%d')


survey_loader_obj = SurveyLoader("app/Data")

# Get the different surveys in json format via a SurveyLoader object.
survey = s[0].contents if (s := survey_loader_obj.get_survey(schema='v2', survey_id='002')) else None
dap = s[0].contents if (s := survey_loader_obj.get_survey(schema='v1', survey_id='283')) else None
feedback = s[0].contents if (s := survey_loader_obj.get_survey(schema='v1', survey_id='139')) else None

with open(f"{SEFT_DIR}/11110000014H_202009_057_20210121143526.xlsx", 'rb') as seft_file:
    seft_bytes = seft_file.read()

output_files = {
        f'{OUTPUT_BUCKET_NAME}/survey/b909aa24-dedc-4d83-be37-8ccf2fdb8314': survey,
        f'{OUTPUT_BUCKET_NAME}/seft/testing_cleanup-seft.xlsx.gpg': seft_bytes,
        f'{OUTPUT_BUCKET_NAME}/dap/c37a3efa-593c-4bab-b49c-bee0613c4fb4.json': dap,
        f'{OUTPUT_BUCKET_NAME}/comments/{comment_filename()}.zip': 'comment',
        f'{OUTPUT_BUCKET_NAME}/feedback/testing_cleanup_feedback-fb-1645465208': feedback
}
input_files = {
        f'{INPUT_SURVEY_BUCKET}/b909aa24-dedc-4d83-be37-8ccf2fdb8314': survey,
        f'{INPUT_SEFT_BUCKET}/testing_cleanup-seft.xlsx.gpg': seft_bytes,
        f'{INPUT_SURVEY_BUCKET}/c37a3efa-593c-4bab-b49c-bee0613c4fb4': dap,
        f'{INPUT_SURVEY_BUCKET}/testing_cleanup_feedback': feedback
}

fake_surveys = ['001', '002', '003', '004', '005']


dap_response = {
  "files": [
    {
      "md5sum": "11a3d51f6145a68beaf2b76684e6e7c5",
      "relativePath": "",
      "scanFileSize": 74657,
      "scanID": "bad4dd615fd9431d82fb77927489be27",
      "scanTime": 5,
      "scanMD5": "11a3d51f6145a68beaf2b76684e6e7c5",
      "name": "a148ac43-a937-401f-1234-b9bc5c123b5a",
      "scanSHA1": "ff0320264a0338866fb42b7765693a0709f88425",
      "scanFileUploadTime": "2021-11-18T13:10:43.732+00:00",
      "scanFileType": "application/zip",
      "sizeBytes": 74657,
      "scanSHA256": "e5ee35349bdb9f79f378437124fb3a9237f888cfb92029b2ad4c9d544510ba8a"
    }
  ],
  "iterationL1": "2110",
  "description": "228 survey response for period 2110 sample unit 48806979667T",
  "sensitivity": "High",
  "tdzComplete": "2021-11-18T13:10:59+0000",
  "manifestCreated": "2021-11-18T13:10:41.946Z",
  "sourceName": "sdx_prod",
  "iterationL2": "",
  "iterationL4": "",
  "dataset": "228|survey/a148ac43-a937-401f-1234-b9bc5c123b5a",
  "version": 1,
  "iterationL3": "",
  "schemaVersion": 1
}
