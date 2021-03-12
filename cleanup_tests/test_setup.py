import unittest

from datetime import datetime, date, timedelta
from app.store import writer
from cleanup_tests import test_data, ignore_warnings
from comment_tests.test_setup import create_entity, cleanup_datastore


class TestCleanupSetup(unittest.TestCase):
    """
    This test class inserts data into both buckets and Datastore and then publishes a message onto
    dap-receipt-topic. This should trigger the sdx-cleanup cloud function to then clean up the data we have inserted.
    test_cleanup.py then runs queries to check if the data has in fact been deleted.
    """

    @classmethod
    def setUpClass(cls):
        cleanup_datastore()

    @ignore_warnings
    def test_setup_output_bucket(self):
        """
        Upload data to buckets in ons-sdx-{{project_id}}
        """
        for data, filename in test_data.items():
            bucket = filename.split('/', 1)[0]
            if 'sefts' in bucket:
                filename = filename.split('/')[2]
            else:
                filename = filename.split('/', 1)[1]
            writer.write(data, filename, bucket)
            print(f'Successfully put data in {bucket}/{filename}')

    @ignore_warnings
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
