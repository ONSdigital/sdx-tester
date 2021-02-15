import unittest
import uuid

from app import survey_loader
from app.messaging import message_manager
from app.tester import run_survey


class TestSurveys(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        message_manager.start()

    @classmethod
    def tearDownClass(cls):
        message_manager.stop()

    def tearDown(self):
        print('-----------------------------------------------------')

    def run_with_survey(self, surveys: dict, receipt: bool, multiple_files: bool):
        for key, survey in surveys.items():
            tx_id = str(uuid.uuid4())
            survey['tx_id'] = tx_id
            with self.subTest(msg=f'test {key} with tx_id: {tx_id}'):
                print('---------------------------------------------------------')
                print(f'testing {key} with tx_id: {tx_id}')
                result = run_survey(message_manager, survey)
                print(str(result))
                self.assertFalse(result.timeout, f'{key} has timed out!')
                self.assertIsNone(result.quarantine, f'{key} has been quarantined!')
                self.assertIsNotNone(result.dap_message, f'{key} did not post dap message!')

                if multiple_files:
                    self.assertTrue(len(result.files) > 1, f'{key} should have produced multiple files!')
                else:
                    self.assertTrue(len(result.files) == 1, f'{key} should have produced one file only!')

                if receipt:
                    self.assertIsNotNone(result.receipt, f'{key} did not produce receipt!')

    def test_dap(self):
        surveys = survey_loader.get_dap()
        self.run_with_survey(surveys, receipt=True, multiple_files=False)

    # def test_legacy(self):
    #     surveys = survey_loader.get_legacy()
    #     failing = ["092", "139"]
    #     for f in failing:
    #         surveys.pop(f)
    #
    #     self.run_with_survey(surveys, receipt=True, multiple_files=True)

    # def test_feedback(self):
    #     surveys = survey_loader.get_feedback()
    #     self.run_with_survey(surveys, receipt=False, multiple_files=False)
