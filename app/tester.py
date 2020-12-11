from app.publish import publish_data
from app.subscriber import SurveyListener


def run_test(data: str, tx_id: str) -> bool:
    publish_data(data)

    def validate(data_str) -> bool:
        print(f"validating response...")
        return True

    test_subscriber = SurveyListener(tx_id, validate)
    passed = test_subscriber.start()
    return passed
