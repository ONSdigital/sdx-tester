"""
Tester.py contains
some of the entry points
for the application, most of the functions
and classes in this file are used in routes.py
"""
import json
import threading
from datetime import datetime
import structlog
import base64
from app import message_manager, socketio
from app.gpg.encryption import encrypt_seft
from app.store import reader, INPUT_SURVEY_BUCKET
from app.jwt.encryption import encrypt_survey
from app.messaging.manager import MessageManager
from app.result import Result
from app.store.writer import write_seft, write


logger = structlog.get_logger()


def run_survey(messenger: MessageManager, survey_dict: dict) -> Result:
    """
    This function puts the encrypted outputs (comments, survey,dap and feedback) in the GCP outputs bucket '{PROJECT_ID}-outputs'
    """
    eq_v3 = True
    encrypted_survey = encrypt_survey(survey_dict)
    tx_id = survey_dict['tx_id']

    write(encrypted_survey, tx_id, INPUT_SURVEY_BUCKET)

    result = Result(tx_id)
    requires_receipt = "feedback" not in survey_dict['type']
    # Should the data be published to pubsub?
    result = messenger.submit(result, encrypted_survey, requires_receipt=requires_receipt, requires_publish=False)

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
    result = message_manager.submit(result, message_str, is_seft=True, requires_publish=True)
    if result.dap_message:
        file_path = result.dap_message.attributes.get('gcs.key')
        file_path = file_path.replace("|", "/")
        file_list = reader.get_files(file_path)
        result.set_files(file_list)
    return result


def decode_files_and_images(response_files: dict):
    """
    For our tester we want to display the data that has been sent through our system. As SDX produces different
    file types they require different processing for our HTML page to display them correctly.
    """
    sorted_files = {}
    for key, value in response_files.items():
        if value is None:
            return response_files
        elif key == 'SEFT':
            return {key: 'Seft recieved'}
        elif key.lower().endswith(('jpg', 'png')):
            b64_image = base64.b64encode(value).decode()
            sorted_files[key] = b64_image
        elif type(value) is bytes:
            sorted_files[key] = value.decode('utf-8')
        else:
            sorted_files[key] = value
    return sorted_files


class UserSurveySubmissionsManager:
    """
    Keep control of the submitted
    surveys and their responses
    """
    def __init__(self):
        self.surveys = []

    def __iter__(self):
        """
        Make this object iterable
        and loop over each survey
        """
        for survey in self.surveys:
            yield survey

    def remove_survey(self, tx_id):
        """
        Remove a certain survey
        from this manager
        """
        for survey in list(self.surveys):
            if survey.tx_id == tx_id:
                return self.surveys.pop(survey)

    def process_survey(self, survey):
        """
        Store this survey in the class
        and then kick off a thread to process
        it
        """
        self.surveys.insert(0, survey)
        threading.Thread(target=survey.process_downstream_data).start()

    def get_response(self, tx_id):
        """
        Fetch a response for a user submitted
        survey given the tx_id
        """
        for survey in self.surveys:
            if survey.tx_id == tx_id:
                return survey.response

    def get_all_responses(self):
        return [survey.response for survey in self.surveys]


class UserSurveySubmission:
    """
    Class used for tracking
    a submission made by the
    user
    """
    def __init__(self, tx_id, survey_id, instrument_id, downstream_dict):
        self.tx_id = tx_id
        self.survey_id = survey_id
        self.instrument_id = instrument_id
        self.time_submitted = datetime.now().strftime("%H:%M")
        self.response = None
        self.downstream_dict = downstream_dict

    def process_downstream_data(self):
        """
        The function that processes the data for the submitted
        survey
        """
        self.response = run_survey(message_manager, self.downstream_dict)
        self._log_processed_survey()

    def _log_processed_survey(self):
        socketio.emit('data received', {'response': 'Emitting....'})
        logger.info(f'Emit data (websocket) for {self.tx_id}')


class UserSeftSurveySubmission(UserSurveySubmission):
    """
    A child class used for SEFT submissions
    This class requires the
    downstream_dict -> the json response dictionary
    downstream_data -> the byte data for this SEFT
    """
    def __init__(self, tx_id, survey_id, instrument_id, downstream_dict, downstream_data):
        self.downstream_data = downstream_data
        UserSurveySubmission.__init__(self, f"seft_{tx_id}", survey_id, instrument_id, downstream_dict)

    def process_downstream_data(self):
        """
        The function that processes the data for a SEFT
        submission
        """
        self.response = run_seft(message_manager, self.downstream_dict, self.downstream_data)
        self._log_processed_survey()
