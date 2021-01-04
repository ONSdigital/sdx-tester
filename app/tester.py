from app import store_reader
from app.encryption import encrypt_survey, view_zip_content
from app.messaging.manager import MessageManager, MessageState
from app.result import Result


def run_test(message_manager: MessageManager, survey_dict: dict) -> bool:
    tx_id = survey_dict['tx_id']
    encrypted_survey = encrypt_survey(survey_dict)
    result = Result(survey_dict)
    result = message_manager.submit(result, encrypted_survey)
    print(result)

    if result.dap_message is not None:

        file_data = store_reader.read(tx_id)
        view_zip_content(file_data)
        return True

    else:
        return False
