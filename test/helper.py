import uuid

from app import store_reader
from app.encryption import encrypt_survey
from app.messaging import message_manager, MessageManager
from app.result import Result
from app.tester import run_test
from app.read_data import extract_test_data_list


def run_tests_all(data_location: str):
    survey_results = []
    submissions = extract_test_data_list(data_location)
    for submission in submissions:
        tx_id = str(uuid.uuid4())
        submission['tx_id'] = tx_id
        survey_results.append(downstream(submission))

    return survey_results


def run_test_helper(submission: dict):
    tx_id = str(uuid.uuid4())
    submission['tx_id'] = tx_id
    return downstream(submission)


def downstream(submission: dict):
    try:
        survey_id = f"{submission['survey_id']}.{submission['collection']['instrument_id']}"
    except KeyError as e:
        survey_id = "Error finding survey_id"
        # print(e)
    survey_result = {'survey_id': survey_id,
                     'Dap': None,
                     'Receipt': None,
                     'Quarantined': False,
                     'Timeout': False}
    result = run_test(message_manager, submission)

    if result.dap_message:
        survey_result['Dap'] = 'Passed'
    if result.receipt:
        survey_result['Receipt'] = 'Passed'
    if result.quarantine:
        # survey_result['Quarantined'] = decrypt_survey(result.quarantine.data)
        survey_result['Quarantined'] = True
    if result.timeout:
        survey_result['Timeout'] = True

    return survey_result