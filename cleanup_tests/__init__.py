import warnings
from datetime import datetime

from app.store import OUTPUT_BUCKET_NAME, INPUT_SEFT_BUCKET


def comment_filename():
    date_time = datetime.utcnow()
    return date_time.strftime('%Y-%m-%d')


test_data = {
    'Survey': f'{OUTPUT_BUCKET_NAME}/survey/testing_cleanup_function-survey',
    'seft': f'{OUTPUT_BUCKET_NAME}/seft/testing_cleanup_function-seft',
    'dap': f'{OUTPUT_BUCKET_NAME}/dap/testing_cleanup_function-dap',
    'legacy': f'{OUTPUT_BUCKET_NAME}/legacy/testing_cleanup_function-legacy',
    'seft-input': f'{INPUT_SEFT_BUCKET}/seft/testing_cleanup_function-seft',
    'comment': f'{OUTPUT_BUCKET_NAME}/comments/{comment_filename()}.zip'
}


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            test_func(self, *args, **kwargs)

    return do_test
