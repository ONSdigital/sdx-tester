import unittest
import uuid

from app.messaging import MessageManager
from app.tester import run_survey


class TestQuarantine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.message_manager = MessageManager()

    @classmethod
    def tearDownClass(cls):
        cls.message_manager.shut_down()

    def setUp(self):
        self.survey = {
            "collection": {
                "exercise_sid": "478d806c-f7e2-4fc5-bcde-82148bab029a",
                "instrument_id": "0201",
                "period": "201605"
            },
            "data": {
                "40": "1234500",
                "49": "55",
                "146": "Yes",
                "d12": "Yes",
                "d40": "Yes"
            },
            "flushed": False,
            "metadata": {
                "ref_period_end_date": "2016-05-31",
                "ref_period_start_date": "2016-05-01",
                "ru_ref": "34650525171T",
                "user_id": "UNKNOWN"
            },
            "origin": "uk.gov.ons.edc.eq",
            "started_at": "2018-08-08T11:41:07.910422+00:00",
            "submitted_at": "2018-08-08T11:41:46.463875+00:00",
            "survey_id": "009",
            "tx_id": "9db49fb8-4bcc-4615-b42c-b2ab80b234b8",
            "case_id": "4c0bc9ec-06d4-4f66-88b6-2e42b79f17b3",
            "type": "uk.gov.ons.edc.eq:surveyresponse",
            "version": "0.0.1"
        }

    def tearDown(self):
        print('-----------------------------------------------------')

    def run_with_survey(self, survey: dict):
        key = f"009.0201"
        tx_id = str(uuid.uuid4())
        survey['tx_id'] = tx_id
        print('---------------------------------------------------------')
        print(f'testing {key} with tx_id: {tx_id}')
        result = run_survey(self.message_manager, survey)
        print(str(result))
        self.assertFalse(result.timeout, f'{key} has timed out!')
        self.assertIsNotNone(result.quarantine, f'{key} should have been quarantined!')
        self.assertIsNone(result.dap_message, f'{key} should not post dap message!')
        self.assertIsNone(result.receipt, f'{key} should not produce a receipt!')

    def test_missing_survey_id(self):
        self.survey.pop('survey_id')
        self.run_with_survey(self.survey)

    def test_missing_ru_ref(self):
        self.survey.get('metadata').pop('ru_ref')
        self.run_with_survey(self.survey)

    def test_data_field_missing(self):
        self.survey.pop('data')
        self.run_with_survey(self.survey)

    def test_missing_metadata(self):
        self.survey.pop('metadata')
        self.run_with_survey(self.survey)

    def test_missing_type(self):
        self.survey.pop('type')
        self.run_with_survey(self.survey)
