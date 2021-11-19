import unittest
import uuid

from app import survey_loader
from app import message_manager
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

    def execute(self, survey_dict: dict, receipt: bool, multiple_files: bool, eq_version_3: bool = False):
        for key, survey_list in survey_dict.items():
            for survey in survey_list:
                tx_id = str(uuid.uuid4())
                survey['tx_id'] = tx_id
                with self.subTest(msg=f'test {key} with tx_id: {tx_id}'):
                    print('---------------------------------------------------------')
                    print(f'testing {key} with tx_id: {tx_id}')
                    result = run_survey(message_manager, survey, eq_version_3)
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

                    print("PASSED")

    def test_dap(self):
        surveys = survey_loader.get_dap()
        self.execute(surveys, receipt=True, multiple_files=False)

    def test_survey(self):
        surveys = survey_loader.get_survey()
        self.execute(surveys, receipt=True, multiple_files=True)

    def test_hybrid(self):
        surveys = survey_loader.get_hybrid()
        self.execute(surveys, receipt=True, multiple_files=True)

    def test_feedback(self):
        survey = survey_loader.get_feedback()
        self.execute(survey, receipt=False, multiple_files=False)

    # def test_eq_v3(self):
    #     survey = survey_loader.get_eq_v3_survey()
    #     self.execute(survey, receipt=False, multiple_files=False, eq_version_3=True)
