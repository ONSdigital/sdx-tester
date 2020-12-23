import os
import json


def extract_test_data():
    list_of_test_surveys = []
    path = 'app/Data/surveys'
    print(os.getcwd())
    for x in os.listdir(path):
        print(os.getcwd())
        with open(f'{path}/{x}', 'r') as data:
            list_of_test_surveys.append(json.load(data))
    return list_of_test_surveys
