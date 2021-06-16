import json

from app.gpg.encryption import encrypt_seft
from app.store import reader
from app.jwt.encryption import encrypt_survey
from app.messaging.manager import MessageManager
from app.result import Result
from app.store.writer import write_seft


def run_survey(message_manager: MessageManager, survey_dict: dict) -> Result:
    """
    This function puts the encrypted outputs (comments, survey,dap and feedback) in the GCP outputs bucket '{PROJECT_ID}-outputs'
    """
    encrypted_survey = encrypt_survey(survey_dict)
    result = Result(survey_dict['tx_id'])
    print(f"Result in run_survey is {result}")
    requires_receipt = "feedback" not in survey_dict['type']
    result = message_manager.submit(result, encrypted_survey, requires_receipt=requires_receipt)
    print(f"Result in run_survey is {result}")
    if result.dap_message:
        file_path = result.dap_message.attributes.get('gcs.key')
        # Changes to file path as Nifi can't handle the earlier form
        file_path = file_path.replace("|", "/")
        file_list = reader.get_files(file_path)
        result.set_files(file_list)
    return result


def run_seft(message_manager: MessageManager, message: dict, seft_data: bytes) -> Result:
    """
    This function puts the encrypted seft output in the GCP output bucket '{PROJECT_ID}-outputs'
    and GCP seft-responses bucket '{PROJECT_ID}-seft-responses'
    """
    encrypted_seft = encrypt_seft(seft_data)
    write_seft(encrypted_seft, message['filename'])
    result = Result(message['tx_id'])
    print(f"Result in run_seft is {result}")
    message_str = json.dumps(message)
    print(f"message_str in run_seft is: {message_str}")
    result = message_manager.submit(result, message_str, is_seft=True)
    print(f"Result in run_seft is {result}")
    if result.dap_message:
        file_path = result.dap_message.attributes.get('gcs.key')
        file_path = file_path.replace("|", "/")
        file_list = reader.get_files(file_path)
        result.set_files(file_list)
    return result
