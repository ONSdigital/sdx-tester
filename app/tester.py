from app import store_reader
from app.encryption import encrypt_survey
from app.messaging.manager import MessageManager
from app.result import Result


def run_test(message_manager: MessageManager, survey_dict: dict) -> Result:
    encrypted_survey = encrypt_survey(survey_dict)
    result = Result(survey_dict)
    result = message_manager.submit(result, encrypted_survey)
    if result.dap_message:
        file_path = result.dap_message.attributes.get('gcs.key')
        file_list = store_reader.get_files(file_path)
        result.set_files(file_list)
    return result
