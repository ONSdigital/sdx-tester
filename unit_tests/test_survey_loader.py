"""
Tests for the survey_loader.py
02/02/23

NOTE: when these tests run, they will
also run any top level code in the app files
"""
import unittest

from app import CONFIG
from app.survey_loader import SurveyLoader, Survey, Seft, InvalidSurveyException


class TestSurveyLoader(unittest.TestCase):

	def setUp(self) -> None:
		self.loader = SurveyLoader(CONFIG.DATA_FOLDER)

	def test_read_all(self):
		self.loader.to_json()


class TestSurvey(unittest.TestCase):

	def test_determine_schema_survey_eq_v2(self):
		file_path = f"{CONFIG.DATA_FOLDER}/v1/survey/eq_v2/009.0167.json"
		self.survey = Survey.from_file(file_path)

		expected_schema = "v1"
		actual_schema = self.survey.schema
		self.assertEqual(expected_schema, actual_schema)

	def test_extract_survey_id_json(self):
		file_path = f"{CONFIG.DATA_FOLDER}/v1/survey/eq_v2/009.0167.json"
		self.survey = Survey.from_file(file_path)

		expected_code = "009"
		actual_code = self.survey.survey_id
		self.assertEqual(expected_code, actual_code)

	def test_extract_instrument_id(self):
		file_path = f"{CONFIG.DATA_FOLDER}/v1/survey/eq_v2/009.0167.json"
		survey = Survey.from_file(file_path)

		expected_code = "0167"
		actual_code = survey.extract_instrument_id()
		self.assertEqual(expected_code, actual_code)

	def test_invalid_survey(self):

		# A json with lots of missing information
		test_json = {
			"case_id": "8fc3eb0b-2dd7-4acd-a354-5d4f69503233",
			"tx_id": "bddbb412-75ea-43ce-9efa-0deb07cb8550",
			"survey_metadata": {
				"period_id": "201605",
			},
		}

		with self.assertRaises(InvalidSurveyException):
			Survey(test_json)


class TestSeft(unittest.TestCase):

	def test_extract_survey_id_json(self):
		file_path = f"{CONFIG.DATA_FOLDER}/v1/seft/11110000014H_202009_057_20210121143526.xlsx"
		self.survey = Seft.from_file(file_path)

		expected_code = "seft_057"
		actual_code = self.survey.survey_id
		self.assertEqual(expected_code, actual_code)

	def test_extract_seft_instrument_id(self):
		file_path = f"{CONFIG.DATA_FOLDER}/v1/seft/11110000014H_202009_057_20210121143526.xlsx"
		self.survey = Seft.from_file(file_path)

		# TODO do sefts have instrument id?
		print()

if __name__ == '__main__':
	unittest.main()
