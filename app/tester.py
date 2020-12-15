from app import store_reader
from app.encryption import encrypt_survey, decrypt_survey
from app.publish import publish_data
from app.subscriber import SurveyListener


def run_test(data: dict, tx_id: str) -> bool:
    encrypted_survey = encrypt_survey(data)
    publish_data(encrypted_survey, tx_id)

    def validate(tx_id) -> bool:
        # file_name = store_reader.get_filename(message_str)
        file_data = store_reader.read(tx_id)
        print(f"validating response...")
        print(decrypt_survey(file_data))
        return True

    test_subscriber = SurveyListener(tx_id, validate)
    passed = test_subscriber.start()
    print(passed)
    return passed
