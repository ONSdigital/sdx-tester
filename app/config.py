"""
Config.py

contains classes and function used to setup
the application and store configuration
settings

02/02/23
"""

# Imports
import os


script_dir = os.path.dirname(__file__)


class Config:
	"""
	Class to hold required configuration data
	:param proj_id: The ID for the current project
	:return: None
	"""

	def __init__(self, proj_id) -> None:
		self.PROJECT_ID = proj_id

		# Folders
		self.APP_FOLDER = script_dir
		self.DATA_FOLDER = f"{self.APP_FOLDER}/Data"


