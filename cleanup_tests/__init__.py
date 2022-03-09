from datetime import datetime
from app.store import OUTPUT_BUCKET_NAME, INPUT_SEFT_BUCKET, INPUT_SURVEY_BUCKET


def comment_filename():
    date_time = datetime.utcnow()
    return date_time.strftime('%Y-%m-%d')


output_files = {
    'survey': f'{OUTPUT_BUCKET_NAME}/survey/testing_cleanup-survey',
    'seft': f'{OUTPUT_BUCKET_NAME}/seft/testing_cleanup-seft.xlsx.gpg',
    'dap': f'{OUTPUT_BUCKET_NAME}/dap/testing_cleanup-dap.json',
    'comment': f'{OUTPUT_BUCKET_NAME}/comments/{comment_filename()}.zip',
    'feedback': f'{OUTPUT_BUCKET_NAME}/feedback/testing_cleanup_feeback-fb-1645465208'
}

input_files = {
    'survey-input': f'{INPUT_SURVEY_BUCKET}/testing_cleanup-survey',
    'seft-input': f'{INPUT_SEFT_BUCKET}/testing_cleanup-seft.xlsx.gpg',
    'dap-input': f'{INPUT_SURVEY_BUCKET}/testing_cleanup-dap',
    'feedback-input': f'{INPUT_SURVEY_BUCKET}/testing_cleanup_feeback'
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

