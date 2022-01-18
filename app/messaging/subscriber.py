import structlog

from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
from app.messaging import PROJECT_ID
from app.datastore.datastore_reader import fetch_quarantined_messages
import time

logger = structlog.get_logger()


class Target:
    """
    A class for recording the status of a received message
    """

    def __init__(self) -> None:
        self.complete = False
        self._message = None

    def is_complete(self):
        return self.complete

    def set_complete(self):
        self.complete = True

    def set_message(self, message):
        self._message = message

    def get_message(self):
        return self._message


class BaseListener:
    """
    A base class containing the required methods to manage a set of targets
    """

    def __init__(self, label: str):
        self.label = label
        self.targets = {}

    def add_target(self, tx_id, target: Target):
        """
        Add a specific tx_id from the targets dictionary
        """
        logger.info(f"Added {tx_id} to targets on {self.label}")
        self.targets[tx_id] = target

    def remove_target(self, tx_id):
        """
        Remove a specific tx_id from the targets dictionary
        """
        if tx_id in self.targets:
            logger.info(f"Removed {tx_id} to targets on {self.label}")
            del self.targets[tx_id]

    def remove_all(self):
        self.targets = {}

    def start(self):
        pass

    def stop(self):
        pass


class PubsubListener(BaseListener):
    """
    Class for checking PubSub Subscriptions for quarantined submissions
    """

    def __init__(self, subscription_id: str) -> None:
        super().__init__(subscription_id)
        self.subscription_id = subscription_id
        self.subscriber = pubsub_v1.SubscriberClient()
        self.streaming_pull_future = None

    def _on_message(self, message):
        logger.info(f'Current tx_ids: {self.targets.keys()}')
        tx_id = message.attributes.get('tx_id')
        logger.info(f"Received tx_id from header {tx_id} on {self.label}")
        if tx_id in self.targets:
            message.ack()
            logger.info(f"Acking message with tx_id {tx_id}")
            listener = self.targets[tx_id]
            listener.set_complete()
            listener.set_message(message)
        else:
            message.ack()
            logger.error(f"NOT EXPECTED! acking message with tx_id {tx_id}")
            logger.error(f"Remaining keys: {self.targets.keys()}")

    def start(self):
        """
        Begin listening to the pubsub subscription.

        This functions spawns new threads that listen to the subscription topic and
        on receipt of a message invoke the callback function

        The main thread blocks indefinitely unless the connection times out
        """
        self.subscriber = pubsub_v1.SubscriberClient()
        subscription_path = self.subscriber.subscription_path(PROJECT_ID, self.subscription_id)
        self.streaming_pull_future = self.subscriber.subscribe(subscription_path, callback=self._on_message)
        logger.info(f"Listening for messages on {subscription_path}..\n")

        # Wrap subscriber in a 'with' block to automatically call close() when done.
        with self.subscriber:
            try:
                # When `timeout` is not set, result() will block indefinitely,
                # unless an exception is encountered first.
                self.streaming_pull_future.result()
            except TimeoutError:
                self.streaming_pull_future.cancel()

    def stop(self):
        self.streaming_pull_future.cancel()
        self.subscriber.close()


class DatastoreListener(BaseListener):
    """
    Class for checking DataStore for quarantined submissions
    """

    def __init__(self):
        super().__init__("quarantineChecker")
        # Boolean to enable polling of datastore
        self.enabled = False
        # Interval before polling datastore again (seconds)
        self.poll_interval = 5

    def _check_for_listener_match(self, messages: list):
        """
        Checks for a matching tx_id in list of listeners and messages param
        @param messages: List of tx_id's
        """

        logger.info(f'Current tx_ids: {self.targets.keys()}')
        for target in self.targets:
            if target in messages:
                logger.info(f"Found datastore entity matching listener {target}")
                current_listener = self.targets[target]
                current_listener.set_complete()
                current_listener.set_message(target)

    def stop(self):
        """
        Stop polling datastore for new
        messages
        """
        self.enabled = False

    def start(self):
        """
        Start checking datastore
        for new messages
        """
        self.enabled = True
        while self.enabled:
            self._check_for_listener_match(fetch_quarantined_messages())
            time.sleep(self.poll_interval)
