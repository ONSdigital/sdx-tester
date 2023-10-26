"""
Script to convert the test data
from v1 to v2 schema
"""
import os


def get_all_v1_files() -> list[str]:
	"""
	Collect all the file paths for v1 data
	"""
	v1_path = "../../app/Data"
	all_v1_files = []
	for folder, sub_folder, filenames in os.walk(v1_path):
		for filename in filenames:
			file_path = os.path.join(folder, filename)
			if filename.endswith("json"):
				all_v1_files.append(file_path)

	return all_v1_files


SAME = None


class Mapper:

	def __init__(
			self,
			destination: list = SAME,
			rename: str = SAME,
			mappers: dict = None,
			preserve=True,
			required=True):
		self.destination = destination
		self.rename = rename
		self.mappers = mappers
		self.preserve = preserve
		self.required = required




required_v1 = [
	"tx_id",
	"type",
	"version",
	"origin",
	"survey_id",
	"submitted_at",
	"collection",
	"metadata",
	"data"
]

required_v2 = [
	"tx_id",
	"type",
	"version",
	"data_version",
	"origin",
	"flushed",
	"submitted_at",
	"launch_language_code",
	"collection_exercise_sid",
	"case_id",
	"survey_metadata",
	"data"
],

# TODO collection
v1_to_v2_map = {
	"case_id": Mapper(),
	"tx_id": Mapper(),
	"type": Mapper(),
	"version": Mapper(rename="data_version"),
	"origin": Mapper(),
	"metadata": Mapper(rename="survey_metadata"),
	"survey_id": Mapper(["survey_metadata"]),
	"data": Mapper(),
	"collection": Mapper(preserve=False, mappers={
		"exercise_sid": Mapper(rename="collection_exercise_sid"),
		"schema_name": Mapper(),
		"instrument_id": Mapper(["survey_metadata"], rename="form_type"),
		"period": Mapper(["survey_metadata"], rename="period_id"),
	}),
	"flushed": Mapper(required=False),
	"started_at": Mapper(required=False),
	"submission_language_code": Mapper(required=False)
}


def transform_v1_to_v2(v1_data: dict) -> dict:
	v2 = {}
	required_v2 = ["tx_id", ""]
