import os
import json


# def extract_test_data():
#     list_of_test_surveys = []
#     path = 'app/Data/surveys'
#     for x in os.listdir(path):
#         with open(f'{path}/{x}', 'r') as data:
#             list_of_test_surveys.append(json.load(data))
#     return list_of_test_surveys


def extract_test_data():
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
