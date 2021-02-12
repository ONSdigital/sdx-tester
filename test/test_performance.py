import json
import unittest
import uuid

from app import survey_loader
from app.gpg.encryption import encrypt_seft
from app.jwt.encryption import encrypt_survey
from app.messaging.performance import PerformanceManager
from app.messaging.publisher import publish_data, publish_seft
from app.store.writer import write_seft

SEFT_DIR = "app/Data/sefts"


class TestPerformance(unittest.TestCase):

    def test_performance(self):
        data_dict = survey_loader.read_all()
        print(data_dict)
        failing = ["092", "139", 'lms']
        for f in failing:
            data_dict.pop(f)

        total = 0
        # intertwine sefts and surveys
        for survey_id, survey_dict in data_dict.items():
            print(f"starting survey: {survey_id}")

            tx_id = str(uuid.uuid4())
            survey_dict['tx_id'] = tx_id
            encrypted_survey = encrypt_survey(survey_dict)

            print(f"Publishing survey {survey_id} with tx_id: {tx_id}")
            publish_data(encrypted_survey, tx_id)
            total += 1

            seft_message = self.prepare_seft()
            tx_id = seft_message['tx_id']
            print(f"Publishing SEFT {seft_message['survey_id']} with tx_id: {tx_id}")
            message_str = json.dumps(seft_message)
            publish_seft(message_str, tx_id)
            total += 1

        print(f'number of submissions: {total}')
        pm = PerformanceManager()
        pm.start(total)
        pm.stop()

    def prepare_seft(self) -> dict:

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

        encrypted_seft = encrypt_seft(data_bytes)
        write_seft(encrypted_seft, message['filename'])

        return message

