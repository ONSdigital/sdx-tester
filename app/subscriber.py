from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1

from app import project_id, dap_subscription_id

timeout = 20


class SurveyListener:

    def __init__(self, tx_id, validate) -> None:
        super().__init__()
        self.tx_id = tx_id
        self.validate = validate
        self.passed = False

    def callback(self, message):
        tx_id = message.attributes.get('tx_id')
        if tx_id == self.tx_id:
            message.ack()
            print(f"acking message with tx_id {tx_id}")
            self.passed = self.validate(tx_id)
        else:
            message.nack()
            print(f"nacking message with tx_id {tx_id}")
            print(f"continuing to listen ...")

    def start(self) -> bool:

        survey_subscriber = pubsub_v1.SubscriberClient()
        # The `subscription_path` method creates a fully qualified identifier
        # in the form `projects/{project_id}/subscriptions/{subscription_id}`
        dap_subscription_path = survey_subscriber.subscription_path(project_id, dap_subscription_id)

        streaming_pull_future = survey_subscriber.subscribe(dap_subscription_path, callback=self.callback)
        print(f"Listening for {self.tx_id} message on {dap_subscription_path}..\n")

        # Wrap subscriber in a 'with' block to automatically call close() when done.
        with survey_subscriber:
            try:
                # When `timeout` is not set, result() will block indefinitely,
                # unless an exception is encountered first.
                streaming_pull_future.result(timeout)
            except TimeoutError:
                streaming_pull_future.cancel()

        return self.passed
