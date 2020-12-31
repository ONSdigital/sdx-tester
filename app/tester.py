from app import store_reader
from app.encryption import encrypt_survey, view_zip_content
from app.messaging.manager import MessageManager, MessageState


def run_test(message_manager: MessageManager, survey_dict: dict) -> bool:
    tx_id = survey_dict['tx_id']
    encrypted_survey = encrypt_survey(survey_dict)

    result = message_manager.submit(tx_id, encrypted_survey)
    print(result)

    if MessageState.TIMED_OUT in result:
        return False
    elif MessageState.FAILED_SEND in result:
        return False

    file_data = store_reader.read(tx_id)
    # file_data_decrypted = decrypt_zip(file_data)
    view_zip_content(file_data)

    return True
