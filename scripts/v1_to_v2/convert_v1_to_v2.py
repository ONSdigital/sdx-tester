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
			required=True,
			retain=True):
		self.destination = destination
		self.rename = rename
		self.mappers = mappers
		self.preserve = preserve
		self.required = required
		self.retain= retain


v1_to_v2_map = {
	"case_id": Mapper(),
	"tx_id": Mapper(),
	"type": Mapper(),
	"version": Mapper(rename="data_version"),
	"origin": Mapper(),
	"metadata": Mapper(rename="survey_metadata", mappers={
		"ref_period_start_date": Mapper(rename="ref_p_start_date"),
		"ref_period_end_date": Mapper(rename="ref_p_end_date"),
	}),
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
	"submitted_at": Mapper(),
	"submission_language_code": Mapper(),
	"launch_language_code": Mapper(),
}


def deep_merge(dict1, dict2):
	"""Recursively merge dict2 into dict1."""
	for key, value in dict2.items():
		if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
			deep_merge(dict1[key], value)
		else:
			dict1[key] = value
	return dict1


def transform_v1_to_v2(v1_data: dict) -> dict:
	v2_data = {
		"version": "v2",
		"survey_metadata": {
			"ru_name": "Example Business name"
		}
	}

	def process_mapping(src_key, mapping, v1_data_src, v2_data_dest):
		if src_key not in v1_data_src and mapping.required:
			raise ValueError(f"Required key '{src_key}' not found in V1 data.")
		elif src_key not in v1_data_src:
			print("Ignoring: ",src_key, "in data: ",v1_data_src)
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
			mapping_items = []  # Store a list of the mapping items so we can removed the old ones
			for nested_key, nested_mapping in mapping.mappers.items():
				process_mapping(nested_key, nested_mapping, v1_data_src[src_key], nested_v2_data)
				mapping_items.append(nested_key)

			# Copy over all data not specified in mapping
			for k, v in v1_data_src[src_key].items():
				if k not in mapping_items:
					nested_v2_data[k] = v
			if not mapping.preserve:
				# Merge the two dictionaries
				deep_merge(target, nested_v2_data)
			else:
				deep_merge(target[dest_key], nested_v2_data)

		else:
			target[dest_key] = v1_data_src[src_key]


	for key, mapping in v1_to_v2_map.items():
		process_mapping(key, mapping, v1_data, v2_data)

	return v2_data
