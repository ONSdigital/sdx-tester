import os
import json


# def extract_test_data():
#     list_of_test_surveys = []
#     path = '/Users/tomholroyd/sdx-gcp/sdx-tester/app/Data/surveys'
#     for x in os.listdir(path):
#         os.chdir(path)
#         with open(x) as data:
#             survey = str(data.read())
#             list_of_test_surveys.append(survey)
#     return list_of_test_surveys


def extract_test_data():
    list_of_test_surveys = []
    path = '/Users/tomholroyd/sdx-gcp/sdx-tester/app/Data/surveys'
    for x in os.listdir(path):
        os.chdir(path)
        with open(x) as data:
            list_of_test_surveys.append(json.load(data))
    return list_of_test_surveys
