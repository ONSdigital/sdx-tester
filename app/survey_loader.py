import hashlib
import os
import json
import uuid


def read_ui() -> dict:
    sorted_surveys = {}
    result = {k: v[0] for k, v in read_all_v1().items()}
    for key in sorted(result.keys()):
        sorted_surveys[key] = result[key]
    return sorted_surveys


def get_json_surveys() -> dict:
    """
    This function takes the surveys from the
    survey loader, and extracts the data into a dictionary,
    if the survey is SEFT, it will use get_seft_metadata to
    ensure the dictionary can be serialized.
    """

    # Get all v1 surveys
    data_v1 = read_all_v1()

    # Get all v2 surveys
    data_v2 = read_all_v2()

    # Return a dictionary containing all the surveys
    # schema_version: {survey_id: [form1, form2 ...]}
    return {
        "v1": {**{key: val for key, val in sorted(data_v1.items()) if "seft" not in key},
               **{outer_key: [i.get_seft_metadata() for i in outer_val] for outer_key, outer_val in sorted(data_v1.items()) if "seft" in outer_key}},
        "v2": {key: val for key, val in sorted(data_v2.items())}

    }


def read_all_v1() -> dict:
    """
    Returns a dict of list of surveys mapped to their survey_id.
    Contains all types of submission.
    """
    s_dict = get_survey()
    d_dict = get_dap()
    h_dict = get_hybrid()
    f_dict = get_feedback()
    seft_dict = get_seft()
    return {**s_dict, **d_dict, **h_dict, **f_dict, **seft_dict}


def read_all_v2():
    """
    Returns a dict of list of surveys mapped to their survey_id.
    Contains all types of submission.
    """
    s_dict = get_survey_v2()
    d_dict = get_dap(schema_version="v2")
    h_dict = get_hybrid(schema_version="v2")
    f_dict = get_feedback(schema_version="v2")
    seft_dict = get_seft(schema_version="v2")
    return {**s_dict, **d_dict, **h_dict, **f_dict, **seft_dict}


def get_survey() -> dict:
    return _read_survey_type("survey/eq_v2")


def get_survey_v2():
    """
    Get the surveys with scheme version 2
    """
    return _read_survey_type("survey", schema_version="v2")


def get_eq_v3_survey(schema_version="v1") -> dict:
    return _read_survey_type("survey/eq_v3", schema_version)


def get_dap(schema_version="v1") -> dict:
    return _read_survey_type("dap", schema_version)


def get_hybrid(schema_version="v1") -> dict:
    return _read_survey_type("hybrid", schema_version)


def get_feedback(schema_version="v1") -> dict:
    return {f'feedback_{k}': v for k, v in _read_survey_type("feedback", schema_version).items()}


def get_seft(schema_version="v1") -> dict:
    """
    For seft submissions, this method retrieves the seft_name, seft_metadata and seft_bytes with the object of SeftSubmission class.
    Produces a dict of list of survey with the 'seft_(survey_id)' as the key.
    """
    seft_dict = {}
    seft_path = f'app/Data/{schema_version}/seft'
    if os.path.exists(seft_path):
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


def _read_survey_type(survey_type: str, schema_version="v1") -> dict:
    """
    This method produces a dict of list of survey with the survey_id as the key.
    :param survey_type: The type of survey to select (survey, seft etc)
    :param schema_version: The survey schema (v1 or v2)
    """
    survey_dict = {}
    survey_path = f'app/Data/{schema_version}/{survey_type}'
    if os.path.exists(survey_path):
        for filename in os.listdir(survey_path):
            with open(f'{survey_path}/{filename}', 'r') as data:
                survey = json.load(data)
                if schema_version == "v1":
                    key = f"{survey['survey_id']}"
                else:
                    key = f"{survey['survey_metadata']['survey_id']}"
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
    """
    This class hold the seft_name, seft_metadata and seft_bytes for seft submissions.
    """
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
