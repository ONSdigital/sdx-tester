import os
import json


def extract_test_data():
    list_of_test_surveys = []
    path = '/Users/tomholroyd/sdx-gcp/sdx-tester/app/Data/surveys'
    for x in os.listdir(path):
        os.chdir(path)
        with open(x) as data:
            hi = json.loads(data.read())
            list_of_test_surveys.append(hi)
    return list_of_test_surveys


extract_test_data()
