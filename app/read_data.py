import os
import json


def extract_test_data():
    list_of_test_surveys = []
    sdx_home = os.environ.get('SDX_HOME')
    path = f'{sdx_home}/sdx-gcp/sdx-tester/app/Data/surveys'
    for x in os.listdir(path):
        os.chdir(path)
        with open(x) as data:
            list_of_test_surveys.append(json.load(data))
    return list_of_test_surveys
