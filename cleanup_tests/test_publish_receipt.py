import unittest

from app.messaging.publisher import publish_dap_receipt
from cleanup_tests import test_data, ignore_warnings


class TestCleanup(unittest.TestCase):

    @ignore_warnings
    def test_kickoff_cleanup_outputs(self):
        """
        Publishes a PuSub message for each element placed within the bucket.
        """
        test_data.pop('seft-input')
        for data, filename in test_data.items():
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
