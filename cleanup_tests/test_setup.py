import unittest

from datetime import datetime, date, timedelta
from app.messaging.publisher import publish_dap_receipt
from app.store import INPUT_SEFT_BUCKET, OUTPUT_BUCKET_NAME, writer
from comment_tests.test_setup import create_entity


def comment_filename():
    date_time = datetime.utcnow()
    return date_time.strftime('%Y-%m-%d')


class TestCleanup(unittest.TestCase):
    """
    This test class inserts data into both buckets and Datastore and then publishes a message onto
    dap-receipt-topic. This should trigger the sdx-cleanup cloud function to then clean up the data we have inserted.
    test_cleanup.py then runs queries to check if the data has in fact been deleted.

    We do not need to make assertions that data has been successfully stored. The tests would fail and
    throw a google exception
    """

    test_data = {
        'Silly Survey Data': f'{OUTPUT_BUCKET_NAME}/survey/testing_cleanup_function-survey',
        'Silly SEFT Data': f'{OUTPUT_BUCKET_NAME}/seft/testing_cleanup_function-seft',
        'Silly dap Data': f'{OUTPUT_BUCKET_NAME}/dap/testing_cleanup_function-dap',
        'Silly legacy Data': f'{OUTPUT_BUCKET_NAME}/legacy/testing_cleanup_function-legacy',
        'Silly seft-input Data': f'{INPUT_SEFT_BUCKET}/seft/testing_cleanup_function-seft',
        'Silly comment Data': f'{OUTPUT_BUCKET_NAME}/comments/{comment_filename()}.zip'
    }

    def test_setup_output_bucket(self):
        """
        Upload data to buckets in ons-sdx-{{project_id}}
        """
        for data, filename in self.test_data.items():
            bucket = filename.split('/', 1)[0]
            if 'sefts' in bucket:
                filename = filename.split('/')[2]
            else:
                filename = filename.split('/', 1)[1]
            writer.write(data, filename, bucket)
            print(f'Successfully put: {data} in {bucket}')

    def test_setup_comments(self):
        """
        Upload 5 comments to Datastore in ons-sdx-{{project_id}}
        """
        d = date.today()
        today = datetime(d.year, d.month, d.day)
        yesterday = today - timedelta(1)
        for x in range(5):
            survey_id = 'testing_cleanup_function'
            create_entity(survey_id, yesterday)

    def test_kickoff_cleanup_outputs(self):
        """
        Publishes a PuSub message for each element placed within the bucket.
        """
        self.test_data.pop('Silly seft-input Data')
        for data, filename in self.test_data.items():
            print(filename.split('/', 1)[1])
            dap_message = {
                'data': b'Metadata',
                'ordering_key': '',
                'attributes': {
                    "gcs.bucket": filename.split('/', 1)[0],
                    "gcs.key": filename.split('/', 1)[1]
                }
            }
            publish_dap_receipt(dap_message, 'testing_cleanup')
