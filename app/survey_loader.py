import os
import json
import uuid


# This method produces a dict of surveys with the survey_id as the key. This is used for the UI element of SDX-tester
def read_data(filter_func) -> dict:
    dict_of_test_surveys = {}
    sorted_dict = {}
    path = 'app/Data/surveys'
    for filename in os.listdir(path):
        if filter_func(filename):
            with open(f'{path}/{filename}', 'r') as data:
                survey = json.load(data)
                survey_key = f"{survey['survey_id']}-{survey['collection']['instrument_id']}"
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


# This method extracts data for helper.py which gives an automated way of testing all surveys
# path used for all Data 'app/Data/surveys'
def extract_test_data_list(path: str):
    list_of_test_surveys = []
    print(os.getcwd())
    for x in os.listdir(path):
        with open(f'{path}/{x}', 'r') as data:
            survey = json.load(data)
            tx_id = str(uuid.uuid4())
            survey['tx_id'] = tx_id
            list_of_test_surveys.append(survey)
    return list_of_test_surveys
