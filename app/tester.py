import json

from app.gpg.encryption import encrypt_seft
from app.store import reader
from app.jwt.encryption import encrypt_survey
from app.messaging.manager import MessageManager
from app.result import Result
from app.store.writer import write_seft


def run_survey(message_manager: MessageManager, survey_dict: dict) -> Result:
    encrypted_survey = encrypt_survey(survey_dict)
    result = Result(survey_dict['tx_id'])
    result = message_manager.submit(result, encrypted_survey)
    if result.dap_message:
        file_path = result.dap_message.attributes.get('gcs.key')
        file_list = reader.get_files(file_path)
        result.set_files(file_list)
    return result


def run_seft(message_manager: MessageManager, message: dict, seft_data: bytes) -> Result:
    encrypted_seft = encrypt_seft(seft_data)
    write_seft(encrypted_seft, message['filename'])
    result = Result(message['tx_id'])
    message_str = json.dumps(message)
    result = message_manager.submit(result, message_str, is_seft=True)
    if result.dap_message:
        file_path = result.dap_message.attributes.get('gcs.key')
        file_list = reader.get_files(file_path)
        result.set_files(file_list)
    return result
