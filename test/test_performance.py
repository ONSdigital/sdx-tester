import json
import threading
import unittest
import uuid

from app import survey_loader
from app.gpg.encryption import encrypt_seft
from app.jwt.encryption import encrypt_survey
from app.messaging.performance import PerformanceManager
from app.messaging.publisher import publish_data, publish_seft
from app.store.writer import write_seft

SEFT_DIR = "app/Data/sefts"
filename = f"11110000014H_202009_057_20210121143526"


def prepare_seft(data_bytes: bytes, i: int) -> dict:



    message = {
        'filename': f'{filename}_{i}',
        'tx_id': str(uuid.uuid4()),
        'survey_id': '057',
        'period': '202009',
        'ru_ref': '20210121143526',
        'md5sum': '12345',
        'sizeBytes': 42
    }



    encrypted_seft = encrypt_seft(data_bytes)
    write_seft(encrypted_seft, message['filename'])

    return message


class TestPerformance(unittest.TestCase):

    def test_performance(self):

        with open(f"{SEFT_DIR}/{filename}.xlsx", 'rb') as seft_file:
            data_bytes = seft_file.read()

        # get all surveys
        survey_dicts = survey_loader.read_all()

        # remove known failures
        failing = ["092", "139", 'lms']
        for f in failing:
            survey_dicts.pop(f)

        survey_list = list(survey_dicts.values())

        # create more data
        survey_list = survey_list * 5

        total = 0
        seft_count = 0
        data_list = []
        for survey in survey_list:

            # survey
            tx_id = str(uuid.uuid4())
            survey['tx_id'] = tx_id
            data_list.append({'tx_id': tx_id, 'data': encrypt_survey(survey), 'seft': False})

            # seft
            message = prepare_seft(data_bytes, seft_count)
            seft_count += 1
            data_list.append({'tx_id': message['tx_id'], 'data': json.dumps(message), 'seft': True})

            total += 2

        self.data_list = data_list
        pm = PerformanceManager()

        print('')
        print('---------------------------------------------------')
        print(f'Submitting: {total} submissions')
        print('---------------------------------------------------')
        print('')

        t = threading.Thread(target=self.submit_submissions)
        # start publishing
        t.start()
        # start subscribing - this will block
        count, time_in_secs = pm.start(total)

        print('')
        print('---------------------------------------------------')
        print(f'Completed {count} out of {total} submissions in {time_in_secs} seconds')
        print('---------------------------------------------------')
        print('')

        pm.stop()
        t.join()

    def submit_submissions(self):
        for submission in self.data_list:
            tx_id = submission['tx_id']
            data = submission['data']
            seft = submission['seft']
            if seft:
                publish_seft(data, tx_id)
            else:
                publish_data(data, tx_id)
