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


def transform_v1_to_v2(v1_data: dict) -> dict:
	pass
