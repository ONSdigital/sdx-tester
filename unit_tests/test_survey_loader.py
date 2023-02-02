"""
Tests for the survey_loader.py
02/02/23
"""
import json
import unittest

from app import CONFIG
from app.survey_loader import SurveyLoader


class TestSurveyLoader(unittest.TestCase):

	def setUp(self) -> None:
		self.loader = SurveyLoader(CONFIG.DATA_FOLDER)

	def test_information_extraction(self):

		file_path = f"{CONFIG.DATA_FOLDER}/v1/dap/283.0001.json"
		expected_survey_id = "283"
		schema, actual_survey_id, content = self.loader._extract_file_information(file_path)
		self.assertEqual(expected_survey_id, actual_survey_id)

	def test_extract_survey_code(self):

		file_path = f"{CONFIG.DATA_FOLDER}/v2/survey/009.0106.json"
		with open(file_path, 'r') as data:
			survey = json.load(data)
		actual_code = self.loader._extract_survey_code(survey, "v2")
		expected_code = "009"
		self.assertEqual(expected_code, actual_code)

	def test_read_all(self):

		a = self.loader.to_json()
		print(a)


if __name__ == '__main__':
	unittest.main()
