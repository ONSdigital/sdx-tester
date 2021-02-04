import unittest

from test.helper import run_tests_all

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
        results = run_tests_all('test/Data/good_surveys')
        for result in results:
            with self.subTest(result['survey_id']):
                actual = result
                expected['survey_id'] = result['survey_id']
                print(f'expected: {expected} \n'
                      f'actual  : {actual} \n'
                      f'----------------------------------------------------------------------------------------------')
                self.assertEqual(expected, actual)

