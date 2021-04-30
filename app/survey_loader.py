import hashlib
import os
import json
import uuid


# returns a dict of each type with one survey per survey id
def read_ui() -> dict:
    sorted_surveys = {}
    result = {k: v[0] for k, v in read_all().items()}
    for key in sorted(result.keys()):
        sorted_surveys[key] = result[key]
    return sorted_surveys


# returns a dict of list of surveys mapped to their survey_id
# contains all types of submission
def read_all() -> dict:
    s_dict = get_survey()
    d_dict = get_dap()
    h_dict = get_hybrid()
    f_dict = get_feedback()
    seft_dict = get_seft()
    return {**s_dict, **d_dict, **h_dict, **f_dict, **seft_dict}


def get_survey() -> dict:
    return _read_survey_type("survey")


def get_dap() -> dict:
    return _read_survey_type("dap")


def get_hybrid() -> dict:
    return _read_survey_type("hybrid")


def get_feedback() -> dict:
    return {f'feedback_{k}': v for k, v in _read_survey_type("feedback").items()}


def get_seft() -> dict:
    seft_dict = {}
    seft_path = 'app/Data/seft'
    for filename in os.listdir(seft_path):
        with open(f'{seft_path}/{filename}', 'rb') as seft_file:
            seft_bytes = seft_file.read()
            filename = filename.split('.')[0]
            seft = SeftSubmission(
                seft_name=f"seft_{filename}",
                seft_metadata=_seft_metadata(seft_file, filename),
                seft_bytes=seft_bytes
            )
            key = f"seft_{seft.seft_metadata['survey_id']}"
            if key not in seft_dict:
                seft_dict[key] = []
            seft_dict[key].append(seft)

    return seft_dict


# This method produces a dict of list of survey with the survey_id as the key.
def _read_survey_type(survey_type: str) -> dict:
    survey_dict = {}
    survey_path = f'app/Data/{survey_type}'
    for filename in os.listdir(survey_path):
        with open(f'{survey_path}/{filename}', 'r') as data:
            survey = json.load(data)
            key = f"{survey['survey_id']}"
            if key not in survey_dict:
                survey_dict[key] = []
            survey_dict[key].append(survey)
    return survey_dict


def _seft_metadata(seft_file, filename):
    data_bytes = seft_file.read()
    filename_list = filename.split('_')
    survey_id = filename_list[2]
    period = filename_list[1]
    ru_ref = filename_list[3]
    message = {
        'filename': filename,
        'tx_id': str(uuid.uuid4()),
        'survey_id': survey_id,
        'period': period,
        'ru_ref': ru_ref,
        'md5sum': hashlib.md5(data_bytes).hexdigest(),
        'sizeBytes': len(data_bytes),
        'seft': True
    }
    return message


class SeftSubmission:

    def __init__(self, seft_name, seft_metadata, seft_bytes) -> None:
        self.seft_name = seft_name
        self.seft_metadata = seft_metadata
        self.seft_bytes = seft_bytes

    def get_seft_name(self):
        return self.seft_name

    def get_seft_metadata(self):
        return self.seft_metadata

    def get_seft_bytes(self):
        return self.seft_bytes
