from app import store_reader
from app.encryption import encrypt_survey
from app.messaging.manager import MessageManager
from app.result import Result


def run_test(message_manager: MessageManager, survey_dict: dict) -> Result:
    tx_id = survey_dict['tx_id']
    survey_id = survey_dict['survey_id']
    encrypted_survey = encrypt_survey(survey_dict)
    result = Result(survey_dict)
    result = message_manager.submit(result, encrypted_survey)

    if result.dap_message is not None:
        file_list = store_reader.get_files(tx_id, survey_id)
        result.set_files(file_list)
    return result
