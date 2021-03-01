import os
import json


# This method produces a dict of surveys with the survey_id as the key. This is used for the UI element of SDX-tester
def read_data(filter_func) -> dict:
    dict_of_test_surveys = {}
    sorted_dict = {}
    path1 = 'app/Data/surveys'
    path2 = 'app/Data/sefts'
    for filename in os.listdir(path1):
        if filter_func(filename):
            with open(f'{path1}/{filename}', 'r') as data:
                survey = json.load(data)
                # survey_key = f"{survey['survey_id']}-{survey['collection']['instrument_id']}"
                survey_key = f"{survey['survey_id']}"
                dict_of_test_surveys[survey_key] = survey

    for filename in os.listdir(path2):
        with open(f'{path2}/{filename}', 'rb') as seft_file:
            survey_id = filename.split('.')[0]
            seft_key = f'seft_{survey_id}'
            dict_of_test_surveys[seft_key] = seft_file.read()

    for key in sorted(dict_of_test_surveys.keys()):
        sorted_dict[key] = dict_of_test_surveys[key]

    return sorted_dict


def read_all() -> dict:
    return read_data(lambda filename: True)


def get_dap() -> dict:
    dap_ids = ["023", "134", "147", "281", "283"]
    return read_data(lambda filename: filename[0:3] in dap_ids)


def get_legacy() -> dict:
    non_legacy_ids = ["023", "134", "147", "281", "283", "lms"]
    return read_data(lambda filename: filename[0:3] not in non_legacy_ids)


def get_feedback() -> dict:
    return read_data(lambda filename: 'feedback' in filename)


def get_specific(survey_id: str, instrument_id: str):
    return read_data(lambda filename: filename == f'{survey_id}.{instrument_id}.json')
