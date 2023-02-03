"""
Tests for the survey_loader.py
02/02/23
"""
import json
import unittest

from app import CONFIG
from app.survey_loader import SurveyLoader, Survey


class TestSurveyLoader(unittest.TestCase):

	def setUp(self) -> None:
		self.loader = SurveyLoader(CONFIG.DATA_FOLDER)

	def test_read_all(self):
		a = self.loader.to_json()
		print(a)


class TestSurvey(unittest.TestCase):

	def test_determine_schema_survey_eq_v2(self):
		file_path = f"{CONFIG.DATA_FOLDER}/v1/survey/eq_v2/009.0167.json"
		self.survey = Survey(file_path)

		expected_schema = "v1"
		actual_schema = self.survey.schema
		self.assertEqual(expected_schema, actual_schema)

	def test_extract_survey_code_json(self):
		file_path = f"{CONFIG.DATA_FOLDER}/v1/survey/eq_v2/009.0167.json"
		self.survey = Survey(file_path)

		expected_code = "009"
		actual_code = self.survey.survey_code
		self.assertEqual(expected_code, actual_code)

if __name__ == '__main__':
	unittest.main()
