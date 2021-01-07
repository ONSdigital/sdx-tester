import os
import json
import uuid


# This method produces a dict of surveys with the survey_id as the key. This is used for the UI element of SDX-tester
def extract_test_data_dict():
    dict_of_test_surveys = {}
    sorted_dict = {}
    path = 'app/Data/surveys'
    for x in os.listdir(path):
        with open(f'{path}/{x}', 'r') as data:
            survey = json.load(data)
            # survey_key = f"{survey['survey_id']}.{survey['collection']['instrument_id']}"
            survey_key = f"{survey['survey_id']}"
            dict_of_test_surveys[survey_key] = survey
    for key in sorted(dict_of_test_surveys.keys()):
        sorted_dict[key] = dict_of_test_surveys[key]
    return sorted_dict


# This method extracts data for test.py which gives an automated way of testing all surveys
def extract_test_data_list():
    list_of_test_surveys = []
    path = 'app/Data/surveys'
    for x in os.listdir(path):
        with open(f'{path}/{x}', 'r') as data:
            survey = json.load(data)
            tx_id = str(uuid.uuid4())
            survey['tx_id'] = tx_id
            list_of_test_surveys.append(survey)
    return list_of_test_surveys
