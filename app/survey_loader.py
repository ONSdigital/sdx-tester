import hashlib
import os
import json
import uuid
from abc import ABC
from typing import Union, Any

from app import CONFIG

# Defines how to extract certain metadata from the different schemas
# Each item in the array corresponds to a level of the json
schema_logic = {
    "v1": {
        "survey_id": ["survey_id"],
        "instrument_id": ["collection", "instrument_id"]
    },
    "v2": {
        "survey_id": ["survey_metadata", "survey_id"],
        "instrument_id": ["survey_metadata", "form_type"]
    }
}

# Defines a mapping of schema versions, each version
# in the array will get mapped to it's key, eg. 0.0.1 -> v1
determine_schema = {
    "version": {
        "v1": ["0.0.1", "0.0.3"],
        "v2": ["v2"]

    },
}


class InvalidSurveyException(Exception):
    def __init__(self, message="The loaded survey is invalid"):
        self.message = message
        super().__init__(self.message)


class SurveyCore(ABC):
    """
    The Abstract for every
    survey that tester loads
    """
    def __init__(self, contents: json):
        self.contents = contents
        self.schema = self._determine_schema()
        self.survey_id = self._extract_survey_id()

    @classmethod
    def from_file(cls, file_path):
        """
        Load a survey given a path to the file
        """
        return cls(cls._extract_content(cls, file_path))

    def _determine_schema(self) -> str:
        """
        Determine the schema of this file, based
        on the folder it's in
        """

        if "version" not in self.contents:
            raise InvalidSurveyException(message="This survey does not contain a version attribute")

        for version in determine_schema["version"].keys():
            if self.contents["version"] in determine_schema["version"][version]:
                return version

    def _extract_metadata_from_contents(self, key):
        """
        Extract certain metadata from the survey,
        the key must be specified in the schema_logic
        dictionary
        """
        sc = self.contents
        for i in schema_logic[self.schema][key]:
            try:
                sc = sc[i]
            except KeyError:
                raise InvalidSurveyException(message="The format of this survey is incorrect")
        return sc

    def _extract_survey_id(self) -> str:
        """
        Retrieve the survey id
        from the contents of the survey
        """

        try:
            return self._extract_metadata_from_contents("survey_id")
        except InvalidSurveyException:
            raise InvalidSurveyException(message="This survey is missing a survey_id in the correct location")

    def _extract_content(self, file_path: str) -> json:
        """
        Method to load a simple json file
        """
        with open(file_path, 'r') as data:
            contents = json.load(data)
        return contents

    def serialize(self) -> json:
        """
        Convert this survey to a JSON
        format
        """
        return self.contents


class Survey(SurveyCore):
    """
    Class containing logic specific
    to surveys (not SEFT)
    """

    def __init__(self, contents: json):
        super(Survey, self).__init__(contents)

    def extract_instrument_id(self):
        """
        Fetch the instrument_id
        for this survey
        """
        version = self._determine_schema()
        if version == "v2":
            if self.contents.get("channel") == "RH":
                # submissions from RM do not have an instrument_id so default to 0001
                return "0001"
        try:
            return self._extract_metadata_from_contents("instrument_id")
        except InvalidSurveyException:
            raise InvalidSurveyException(message="Could not extract the instrument_id from this survey")


class Seft(SurveyCore):
    """
    Class for storing SEFT data
    """

    def __init__(self, contents: json):
        self.byte_data = None
        self.seft_name = None
        super(Seft, self).__init__(contents)

    @classmethod
    def from_file(cls, file_path):
        return super(Seft, cls).from_file(file_path)

    def _extract_content(self, file_path: str):
        """
        Override the parent class, extract the content
        from a SEFT file
        """
        with open(file_path, 'rb') as seft_file:
            seft_bytes = seft_file.read()
            filename = os.path.basename(file_path).split(".")[0]
            # Save other important data
            self.seft_name = f"seft_{filename}"
            self.byte_data = seft_bytes
            # Assign the content to the metadata
            data = _seft_metadata(seft_file, filename)
        return data

    def _determine_schema(self) -> str:
        """
        For now simply return v1 for all
        SEFTS we find
        """
        return "v1"

    def _extract_survey_id(self) -> str:
        """
        Extract the survey code from the seft
        submission
        """
        return f"seft_{self.contents['survey_id']}"


class SurveyLoader:
    """
    Will load surveys from the filesystem
    """
    def __init__(self, data_folder: str):
        self.data_folder = data_folder

        # Store just the survey objects {schema: {survey_id: Survey} }
        self.files_only = {version: {} for version in schema_logic.keys()}

        # Store the entire structure including recursive sub folders
        # {schema: {survey_type: {sub-folder: Survey}}
        self.all_data = self._read_all(self.data_folder)

    def _read_all(self, root: str):
        """
        Will parse everything in the specified data folder,
        each direct sub folder will be assigned to a schema version (v1, v2)
        and folders under those will be survey types (DAP, SEFT etc)
        :param root The folder to search
        """
        my_dict = {}   # this is the final dictionary to be populated

        # Go through every folder in the current folder
        for element in os.listdir(root):

            if os.path.isfile(os.path.join(root, element)):

                # Create a survey object
                file_path = os.path.join(root, element)
                if "seft" in file_path:
                    survey = Seft.from_file(file_path)
                else:
                    survey = Survey.from_file(file_path)

                # Store just the files

                # Create a list of surveys for this survey code
                if survey.survey_id not in self.files_only[survey.schema]:
                    self.files_only[survey.schema][survey.survey_id] = []

                # Add this survey to the list
                self.files_only[survey.schema][survey.survey_id].append(survey)

                # Store and preserve folder structure

                # Create a list of surveys for this survey code
                if survey.survey_id not in my_dict:
                    my_dict[survey.survey_id] = []

                # Add this survey to the list
                my_dict[survey.survey_id].append(survey)

            elif os.path.isdir(os.path.join(root, element)):
                my_dict[element] = self._read_all(os.path.join(root, element))

        return my_dict

    def to_json(self):
        """
        Convert this data structure to
        a json readable format

        {schema_version: {survey_id: [survey1, survey2...]}}
        """

        # Beautiful
        return {
            version: {survey_id: [survey.serialize() for survey in self.files_only[version][survey_id]] for survey_id in self.files_only[version]} for version in self.files_only
        }

    def get_survey(self, schema: str, survey_id: str) -> Union[bool, list[Survey]]:
        """
        Attempt to get a survey from this loader
        given the schema and survey code
        """
        try:
            return self.files_only[schema][survey_id]
        except KeyError:
            return False


def read_all_v1() -> dict:
    """
    Returns a dict of list of surveys mapped to their survey_id.
    Contains all types of submission.

    This function has been rewritten for the performance tests only
    """

    s = SurveyLoader(CONFIG.DATA_FOLDER)
    return {survey_id: s.files_only["v1"][survey_id][0].serialize() for survey_id in s.files_only["v1"]}


def get_survey() -> dict:
    return _read_survey_type("survey")


def get_dap(schema_version="v1") -> dict:
    return _read_survey_type("dap", schema_version)


def get_hybrid(schema_version="v1") -> dict:
    return _read_survey_type("hybrid", schema_version)


def get_feedback(schema_version="v1") -> dict:
    return {f'feedback_{k}': v for k, v in _read_survey_type("feedback", schema_version).items()}


def _read_survey_type(survey_type: str, schema_version="v1") -> dict:
    """
    This method produces a dict of list of survey with the survey_id as the key.
    :param survey_type: The type of survey to select (survey, seft etc)
    :param schema_version: The survey schema (v1 or v2)
    """
    survey_dict = {}
    survey_path = f'app/Data/{schema_version}/{survey_type}'
    if os.path.exists(survey_path):
        for filename in os.listdir(survey_path):
            with open(f'{survey_path}/{filename}', 'r') as data:
                survey = json.load(data)
                if schema_version == "v1":
                    key = f"{survey['survey_id']}"
                else:
                    key = f"{survey['survey_metadata']['survey_id']}"
                if key not in survey_dict:
                    survey_dict[key] = []
                survey_dict[key].append(survey)
    return survey_dict


def _seft_metadata(seft_file, filename):
    data_bytes = seft_file.read()
    filename_list = filename.split('_')
    survey_id = filename_list[2]
    period = filename_list[1]
    ru_ref = filename_list[3]
    message = {
        'filename': filename,
        'tx_id': str(uuid.uuid4()),
        'survey_id': survey_id,
        'period': period,
        'ru_ref': ru_ref,
        'md5sum': hashlib.md5(data_bytes).hexdigest(),
        'sizeBytes': len(data_bytes),
        'seft': True
    }
    return message
