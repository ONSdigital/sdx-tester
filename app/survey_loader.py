import hashlib
import os
import json
import uuid
from urllib import request


# This method produces a dict of surveys with the survey_id as the key. This is used for the UI element of SDX-tester
def read_survey(filter_func) -> dict:
    dict_of_test_surveys = {}
    survey_path = 'app/Data/surveys'
    for filename in os.listdir(survey_path):
        if filter_func(filename):
            with open(f'{survey_path}/{filename}', 'r') as data:
                survey = json.load(data)
                # survey_key = f"{survey['survey_id']}-{survey['collection']['instrument_id']}"
                survey_key = f"{survey['survey_id']}"
                dict_of_test_surveys[survey_key] = survey

    return dict_of_test_surveys


def read_seft():
    dict_of_test_sefts = {}
    seft_path = 'app/Data/sefts'
    for filename in os.listdir(seft_path):
        with open(f'{seft_path}/{filename}', 'rb') as seft_file:
            seft_bytes = seft_file.read()
            filename = filename.split('.')[0]
            seft = SeftSubmission(
                seft_name=f"seft_{filename}",
                seft_metadata=seft_metadata(seft_file, filename),
                seft_bytes=seft_bytes
            )
            dict_of_test_sefts[f"seft_{seft.seft_metadata['survey_id']}"] = seft

    return dict_of_test_sefts


def seft_metadata(seft_file, filename):
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


def read_all() -> dict:
    return read_survey(lambda filename: True)


def read_UI() -> dict:
    sorted_surveys = {}
    surveys = read_survey(lambda filename: True)
    for key in sorted(surveys.keys()):
        sorted_surveys[key] = surveys[key]
    sefts = read_seft()

    return {**sorted_surveys, **sefts}


def get_dap() -> dict:
    dap_ids = ["023", "134", "147", "281", "283"]
    return read_survey(lambda filename: filename[0:3] in dap_ids)


def get_legacy() -> dict:
    non_legacy_ids = ["023", "134", "147", "281", "283", "lms"]
    return read_survey(lambda filename: filename[0:3] not in non_legacy_ids)


def get_feedback() -> dict:
    return read_survey(lambda filename: 'feedback' in filename)


def get_specific(survey_id: str, instrument_id: str):
    return read_survey(lambda filename: filename == f'{survey_id}.{instrument_id}.json')


class SeftSubmission:

    def __init__(self, seft_name, seft_metadata, seft_bytes) -> None:
        self.seft_name = seft_name
        self.seft_metadata = seft_metadata
        self.seft_bytes = seft_bytes

    def get_seft_name(self):
        return self.seft_name

    def get_seft_metadata(self):
        return self.seft_metadata

    def get_seft_bytes(self):
        return self.seft_bytes
