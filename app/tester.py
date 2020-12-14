from app.encryption import encrypt_survey, decrypt_survey
from app.publish import publish_data
from app.subscriber import SurveyListener


def run_test(data: dict, tx_id: str) -> bool:
    encrypted_survey = encrypt_survey(data)
    publish_data(encrypted_survey, tx_id)

    def validate(data_str) -> bool:
        print(f"validating response...")
        print(decrypt_survey(data_str))
        # return True

    test_subscriber = SurveyListener(tx_id, validate)
    passed = test_subscriber.start()
    return passed
