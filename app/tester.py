import json

from app.gpg.encryption import encrypt_seft
from app.store import reader, INPUT_SURVEY_BUCKET
from app.jwt.encryption import encrypt_survey
from app.messaging.manager import MessageManager
from app.result import Result
from app.store.writer import write_seft, write


def run_survey(message_manager: MessageManager, survey_dict: dict, eq_v3: bool = False) -> Result:
    """
    This function puts the encrypted outputs (comments, survey,dap and feedback) in the GCP outputs bucket '{PROJECT_ID}-outputs'
    :param bool eq_v3: Should this survey be run as if its from Eq_v3 (Written directly to bucket) or Eq_v2 (Pubsub) - True = Eq_v3
    """
    encrypted_survey = encrypt_survey(survey_dict, eq_v3)
    tx_id = survey_dict['tx_id']

    if eq_v3:
        # Writing to a bucket instead of posting on queue
        write(encrypted_survey, tx_id, INPUT_SURVEY_BUCKET)

    result = Result(tx_id)
    requires_receipt = "feedback" not in survey_dict['type']
    # Should the data be published to pubsub?
    requires_publish = not eq_v3
    result = message_manager.submit(result, encrypted_survey, requires_receipt=requires_receipt, requires_publish=requires_publish)

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
    message_str = json.dumps(message)
    result = message_manager.submit(result, message_str, is_seft=True)
    if result.dap_message:
        file_path = result.dap_message.attributes.get('gcs.key')
        file_path = file_path.replace("|", "/")
        file_list = reader.get_files(file_path)
        result.set_files(file_list)
    return result
