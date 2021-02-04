import unittest
import uuid

from app.tester import run_seft
from app.messaging import message_manager


class TestSefts(unittest.TestCase):

    def test_sefts(self):
        seft_dir = "app/Data/sefts"
        filename = "11110000014H_202009_057_20210121143526.xlsx"

        message = {
            'tx_id': str(uuid.uuid4()),
            'survey_id': '057',
            'period': '202009',
            'ru_ref': '20210121143526',
            'md5sum': '12345',
            'sizeBytes': 42
        }

        with open(f"{seft_dir}/{filename}") as seft_file:
            data_bytes = seft_file.read()

        result = run_seft(message_manager, message, data_bytes)

        self.assertTrue(result.dap_message)
        self.assertTrue(len(result.files) == 1)
        self.assertIsNone(result.receipt)
        self.assertIsNone(result.quarantine)
