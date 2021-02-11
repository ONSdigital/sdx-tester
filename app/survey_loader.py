import os
import json


# This method produces a dict of surveys with the survey_id as the key. This is used for the UI element of SDX-tester
def read_data(filter_func) -> dict:
    dict_of_test_surveys = {}
    sorted_dict = {}
    path = 'app/Data/surveys'
    for filename in os.listdir(path):
        if filter_func(filename):
            with open(f'{path}/{filename}', 'r') as data:
                survey = json.load(data)
                # survey_key = f"{survey['survey_id']}-{survey['collection']['instrument_id']}"
                survey_key = f"{survey['survey_id']}"
                dict_of_test_surveys[survey_key] = survey

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
