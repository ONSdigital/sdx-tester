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
	"flushed": Mapper(),
	"started_at": Mapper(),
	"submission_language_code": Mapper(),
	"launch_language_code": Mapper()
}


def transform_v1_to_v2(v1_data: dict) -> dict:
	v2_data = {}

	def process_mapping(src_key, mapping, v1_data_src, v2_data_dest):
		if src_key not in v1_data_src and mapping.required:
			raise ValueError(f"Required key '{src_key}' not found in V1 data.")
		elif src_key not in v1_data_src:
			return  # Key not found and not required, so we skip

		dest_key = mapping.rename if mapping.rename is not SAME else src_key

		if mapping.destination is SAME:
			target = v2_data_dest
		else:
			target = v2_data_dest
			for dest in mapping.destination:
				target = target.setdefault(dest, {})

		if mapping.mappers:
			# Recursively process nested mappers
			nested_v2_data = {}
			for nested_key, nested_mapping in mapping.mappers.items():
				process_mapping(nested_key, nested_mapping, v1_data_src[src_key], nested_v2_data)
			target[dest_key] = nested_v2_data
		else:
			target[dest_key] = v1_data_src[src_key]

		# Check if we should preserve the key in the v2_data
		if not mapping.preserve:
			del v2_data_dest[dest_key]

	for key, mapping in v1_to_v2_map.items():
		process_mapping(key, mapping, v1_data, v2_data)

	return v2_data
