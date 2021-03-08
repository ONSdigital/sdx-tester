import hashlib
import uuid


class Seft():

    def __init__(self, survey_id, data_bytes, metadata):
        self.survey_id = survey_id
        self.data_bytes = data_bytes
        self.metadata = metadata


def seft_message(seft_file, filename_without_extension):
    seft_survey1 = []
    data_bytes = seft_file.read()
    filename_list = filename_without_extension.split('_')
    survey_id = filename_list[2]
    period = filename_list[1]
    ru_ref = filename_list[3]
    message = {
        'filename': filename_without_extension,
        'tx_id': str(uuid.uuid4()),
        'survey_id': survey_id,
        'period': period,
        'ru_ref': ru_ref,
        'md5sum': hashlib.md5(data_bytes).hexdigest(),
        'sizeBytes': len(data_bytes)
    }
    seft = Seft(message['survey_id'], data_bytes, message)
    seft_survey1.append(seft)
    print((seft_survey1[0]))
    return seft_survey1


