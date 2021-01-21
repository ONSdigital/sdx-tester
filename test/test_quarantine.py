import unittest
import uuid

from app.messaging import message_manager
from test.helper import run_tests_all
from app.tester import run_test

"""
Flesh out test_bad_surveys where we individually know what is wrong with each 'bad' survey
"""


class TestAllSurveys(unittest.TestCase):

    def setUp(self):
        data = {
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

    def test_bad_survey(self, survey):
        expected = {
            'survey_id': '',
            'Dap': None,
            'Receipt': None,
            'Quarantined': True,
            'Timeout': False
        }
        actual = run_test(message_manager, survey)
        self.assertEqual(expected, actual)

    def test_missing_survey_id(self):
        tx_id = str(uuid.uuid4())
        self.data['tx_id'] = tx_id
        self.data.pop('survey_id')
        self.test_bad_survey(self.data)
