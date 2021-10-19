from datetime import datetime
from app.store import OUTPUT_BUCKET_NAME, INPUT_SEFT_BUCKET, INPUT_SURVEY_BUCKET


def comment_filename():
    date_time = datetime.utcnow()
    return date_time.strftime('%Y-%m-%d')


test_data = {
    'survey': f'{OUTPUT_BUCKET_NAME}/survey/testing_cleanup_function-survey',
    'seft': f'{OUTPUT_BUCKET_NAME}/seft/testing_cleanup_function-seft.xlsx.gpg',
    'dap': f'{OUTPUT_BUCKET_NAME}/dap/testing_cleanup_function-dap',
    'comment': f'{OUTPUT_BUCKET_NAME}/comments/{comment_filename()}.zip'
}

extra_input = {
    'survey-input': f'{INPUT_SURVEY_BUCKET}/testing_cleanup_function-survey',
    'seft-input': f'{INPUT_SEFT_BUCKET}/testing_cleanup_function-seft.xlsx.gpg',
    'dap-input': f'{INPUT_SURVEY_BUCKET}/testing_cleanup_function-dap'
}

fake_surveys = ['001', '002', '003', '004', '005']
