import unittest

from tests.helper import run_tests_all

"""
This test class is an integration test that....
"""

class TestAllSurveys(unittest.TestCase):

    def test_good_surveys(self):
        expected = {'survey_id': '',
                    'Dap': 'Passed',
                    'Receipt': 'Passed',
                    'Quarantined': False,
                    'Timeout': False}
        results = run_tests_all('tests/Data/good_surveys')
        for result in results:
            with self.subTest(result['survey_id']):
                actual = result
                expected['survey_id'] = result['survey_id']
                print(f'expected: {expected} \n'
                      f'actual  : {actual} \n'
                      f'----------------------------------------------------------------------------------------------')
                self.assertEqual(expected, actual)

    def test_bad_surveys(self):
        expected = {
            'survey_id': '',
            'Dap': None,
            'Receipt': None,
            'Quarantined': True,
            'Timeout': False
                    }
        results = run_tests_all('tests/Data/quarantine_surveys')
        for result in results:
            with self.subTest(result['survey_id']):
                actual = result
                expected['survey_id'] = result['survey_id']
                print(f'expected: {expected} \n'
                      f'actual  : {actual} \n'
                      f'----------------------------------------------------------------------------------------------')
                self.assertEqual(expected, actual)
