import json
import math
import threading
import unittest
import uuid

from app import survey_loader
from app.jwt.encryption import encrypt_survey
from app.messaging.performance import PerformanceManager
from app.messaging.publisher import publish_data, publish_seft
from performance_tests.setup import SEFT_COUNT, SEFT_FILENAME


class TestPerformance(unittest.TestCase):

    def test_performance(self):

        # get all survey
        survey_dicts = survey_loader.read_all_v1()

        survey_list = [v[0] for k, v in survey_dicts.items() if not k.startswith("seft")]

        # create at least as many survey as seft
        survey_list = survey_list * (math.ceil(SEFT_COUNT / len(survey_list)))

        data_list = []
        for i in range(SEFT_COUNT):

            # survey
            tx_id = str(uuid.uuid4())
            survey = survey_list[i]
            survey['tx_id'] = tx_id
            data_list.append({'tx_id': tx_id, 'data': encrypt_survey(survey), 'seft': False})

            # seft
            message = {
                'filename': f'{SEFT_FILENAME}_{i}',
                'tx_id': str(uuid.uuid4()),
                'survey_id': '057',
                'period': '202009',
                'ru_ref': '20210121143526',
                'md5sum': '12345',
                'sizeBytes': 42
            }
            data_list.append({'tx_id': message['tx_id'], 'data': json.dumps(message), 'seft': True})

        self.data_list = data_list
        total = len(data_list)
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
