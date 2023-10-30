"""
Script to convert the test data
from v1 to v2 schema
"""
import json
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_directory))


def get_all_v1_files() -> list[str]:
	"""
	Collect all the file paths for v1 data
	"""

	v1_path = os.path.join(project_root, "app/Data/v1")
	all_v1_files = []
	for folder, sub_folder, filenames in os.walk(v1_path):
		for filename in filenames:
			file_path = os.path.join(folder, filename)
			if filename.endswith("json"):
				all_v1_files.append(file_path)

	return all_v1_files


SAME = None


class Mapper:
	"""
	A very simple class
	for storing mappings from v1 -> v2 recursively
	"""

	def __init__(
			self,
			destination: list = SAME,
			rename: str = SAME,
			mappers: dict = None,
			preserve=True,
			create=False
			):
		self.destination = destination
		self.rename = rename
		self.mappers = mappers
		self.preserve = preserve
		self.create=create


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
	"schema_name": Mapper(create=True),
}


def deep_merge(dict1: dict, dict2: dict) -> dict:
	"""
	Merge dictionary values more than a single leve
	deep
	"""
	for key, value in dict2.items():
		if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
			deep_merge(dict1[key], value)
		else:
			dict1[key] = value
	return dict1


def transform_v1_to_v2(v1_data: dict) -> dict:
	"""
	Take a v1 json and transform
	it into a v2 json
	"""

	# Pre-defined data that is needed in v2
	v2_data = {
		"version": "v2",
		"survey_metadata": {
			"ru_name": "ESSENTIAL ENTERPRISE LTD."
		}
	}

	def process_mapping(src_key: str, mapping: Mapper, v1_data_src: dict, v2_data_dest: dict):
		"""
		The recursive function that maps a single v1 key and value into v2
		"""

		# If a key from the mapping is NOT in the json, skip it
		if src_key not in v1_data_src:
			if mapping.create and src_key not in v2_data_dest:
				v2_data_dest[src_key] = ""
			return

		# Work out if the destination key should be renamed or not
		dest_key: str = mapping.rename if mapping.rename is not SAME else src_key

		# Handle relocation of the data
		if mapping.destination is SAME:
			target = v2_data_dest
		else:
			target = v2_data_dest
			for dest in mapping.destination:
				target = target.setdefault(dest, {})

		# If this mapping has nested mappers, apply them recursively
		if mapping.mappers:

			# Recursively process nested mappers
			nested_v2_data = {}
			mapping_items = []  # Store a list of the mapping items so we can keep other keys
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


def process() -> None:
	"""
	Read all V1 files
	process them into a new location
	"""
	all_files: list[str] = get_all_v1_files()
	new_folder = "v1_new"

	for file_path in all_files:
		filename = os.path.basename(file_path)
		print("Converting: ",filename)
		destination = file_path.replace("v1", new_folder)
		with open(file_path, 'r') as file:
			# Load the JSON content from the file into a dictionary
			data = json.load(file)

		try:
			new_data = transform_v1_to_v2(data)
		except Exception as e:
			print(f"Error transforming {filename}: {e}")
		else:

			# Create any directories as needed
			os.makedirs(os.path.dirname(destination), exist_ok=True)

			with open(destination, 'w') as file:
				# Write the dictionary to the file in JSON format
				json.dump(new_data, file, indent=4)

	print("Conversion complete")


process()
