from app import survey_loader
from integration_tests.test_surveys import TestSurveys


class TestEQv3Surveys(TestSurveys):

    def test_eq_v3(self):
        print("testing eqv3")
        survey = survey_loader.get_eq_v3_survey()
        self.execute(survey, receipt=True, multiple_files=True, eq_version_3=True)
