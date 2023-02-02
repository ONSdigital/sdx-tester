"""
Config.py

contains classes and function used to setup
the application and store configuration
settings

02/02/23
"""

# Imports
from os import path, pardir


ROOT_FOLDER = path.abspath(path.join(path.dirname(path.abspath(__file__)), pardir))


class Config:
	"""
	Class to hold required configuration data
	:param proj_id: The ID for the current project
	:return: None
	"""

	def __init__(self, proj_id) -> None:
		self.PROJECT_ID = proj_id

		# Folders
		self.PROJECT_ROOT = ROOT_FOLDER
		self.APP_FOLDER = f"{self.PROJECT_ROOT}/app"
		self.DATA_FOLDER = f"{self.APP_FOLDER}/Data"


