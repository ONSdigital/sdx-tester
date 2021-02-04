import unittest
from test.helper import downstream


class TestAllSurveys(unittest.TestCase):

    def setUp(self):
        self.data = {
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
        self.expected = {
            'survey_id': '009.0201',
            'Dap': None,
            'Receipt': None,
            'Quarantined': True,
            'Timeout': False
        }

    def test_missing_survey_id(self):
        expected = {
            'survey_id': 'Error finding survey_id',
            'Dap': None,
            'Receipt': None,
            'Quarantined': True,
            'Timeout': False
        }
        self.data.pop('survey_id')
        actual = downstream(self.data)
        self.assertEqual(expected, actual)

    def test_missing_ru_ref(self):
        self.data.get('metadata').pop('ru_ref')
        actual = downstream(self.data)
        self.assertEqual(self.expected, actual)

    def test_data_field_missing(self):
        self.data.pop('data')
        actual = downstream(self.data)
        self.assertEqual(self.expected, actual)

    def test_missing_tx_id(self):
        self.data.pop('tx_id')
        actual = downstream(self.data)
        self.assertEqual(self.expected, actual)

    def test_missing_metadata(self):
        self.data.pop('metadata')
        actual = downstream(self.data)
        self.assertEqual(self.expected, actual)

    def test_missing_type(self):
        self.data.pop('type')
        actual = downstream(self.data)
        self.assertEqual(self.expected, actual)

