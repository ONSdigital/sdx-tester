import unittest
import uuid

from app.messaging.publisher import publish_dap_receipt
from app.store import SEFT_BUCKET, reader
from app.tester import run_seft
from app.messaging import message_manager

SEFT_DIR = "app/Data/sefts"


class TestSefts(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        message_manager.start()

    @classmethod
    def tearDownClass(cls):
        message_manager.stop()

    def test_sefts(self):
        filename = "11110000014H_202009_057_20210121143526"

        message = {
            'filename': filename,
            'tx_id': str(uuid.uuid4()),
            'survey_id': '057',
            'period': '202009',
            'ru_ref': '20210121143526',
            'md5sum': '12345',
            'sizeBytes': 42
        }

        with open(f"{SEFT_DIR}/{filename}.xlsx", 'rb') as seft_file:
            data_bytes = seft_file.read()

        result = run_seft(message_manager, message, data_bytes)

        self.assertIsNotNone(result.dap_message)
        self.assertTrue(len(result.files) == 1)
        self.assertIsNone(result.receipt)
        self.assertIsNone(result.quarantine)

        dap_message = result.dap_message
        publish_dap_receipt(dap_message, message.get('tx_id'))

        filename = '/' + dap_message.attributes.get('gcs.key').split('/')[1]

        reader.read(filename, SEFT_BUCKET)
