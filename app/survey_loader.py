import hashlib
import os
import json
import uuid
from urllib import request


# sorted_survey_dict = {}
# sorted_seft_dict = {}
# combined_sorted_dict = {}


# This method produces a dict of surveys with the survey_id as the key. This is used for the UI element of SDX-tester
def read_survey(filter_func) -> dict:
    dict_of_test_surveys = {}
    sorted_dict = {}
    survey_path = 'app/Data/surveys'
    seft_path = 'app/Data/sefts'
    List_of_surveys = []
    for filename in os.listdir(survey_path):
        if filter_func(filename):
            with open(f'{survey_path}/{filename}', 'r') as data:
                survey = json.load(data)
                # survey_key = f"{survey['survey_id']}-{survey['collection']['instrument_id']}"
                survey_key = f"{survey['survey_id']}"
                dict_of_test_surveys[survey_key] = survey

    for filename in os.listdir(seft_path):
        with open(f'{seft_path}/{filename}', 'rb') as seft_file:
            filename_without_extension = filename.split('.')[0]
            seft_key = f'seft_{filename_without_extension}'
            # message = seft_message(seft_file, filename_without_extension)
            seft_obj = seft_message(seft_file, filename_without_extension)
            dict_of_test_surveys[seft_key] = message

    for key in sorted(dict_of_test_surveys.keys()):
        sorted_dict[key] = dict_of_test_surveys[key]

    return sorted_dict



# def read_seft():
#     dict_of_test_sefts = {}
#     seft_path = 'app/Data/sefts'
#     for filename in os.listdir(seft_path):
#         with open(f'{seft_path}/{filename}', 'rb') as seft_file:
#             filename_without_extension = filename.split('.')[0]
#             seft_key = f'seft_{filename_without_extension}'
#             message = seft_message(seft_file, filename_without_extension)
#             dict_of_test_sefts[seft_key] = message
#
#     for key in sorted(dict_of_test_sefts.keys()):
#         dict_of_test_sefts[key] = dict_of_test_sefts[key]
#
#     return sorted_survey_dict


# def combine_survey_and_seft_dict(sorted_survey_dict, sorted_seft_dict):
#     combined_sorted_dict = sorted_survey_dict | sorted_seft_dict
#     return combined_sorted_dict

def seft_message(seft_file, filename_without_extension):
    data_bytes = seft_file.read()
    filename_list = filename_without_extension.split('_')
    survey_id = filename_list[2]
    period = filename_list[1]
    ru_ref = filename_list[3]
    message = {
        'filename': filename_without_extension,
        'tx_id': str(uuid.uuid4()),
        'survey_id': survey_id,
        'period': period,
        'ru_ref': ru_ref,
        'md5sum': hashlib.md5(data_bytes).hexdigest(),
        'sizeBytes': len(data_bytes)
    }
    return message


def read_all() -> dict:
    return read_survey(lambda filename: True)


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
