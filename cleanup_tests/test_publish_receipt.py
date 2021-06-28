import json
import unittest

from app.messaging.publisher import publish_dap_receipt
from cleanup_tests import test_data


class TestCleanup(unittest.TestCase):

    def test_kickoff_cleanup_outputs(self):
        """
        Publishes a PuSub message for each element placed within the bucket.
        """
        test_data.pop('seft-input')
        for data, filename in test_data.items():
            dap_message = json.dumps({'dataset': f"009|{filename.split('/', 1)[1]}"}).encode()
            publish_dap_receipt(dap_message)
