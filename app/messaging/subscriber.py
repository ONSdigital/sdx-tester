import structlog

from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
from app.messaging import PROJECT_ID
from app.datastore.datastore_reader import fetch_quarantined_messages
import time

logger = structlog.get_logger()


class Listener:

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


class MessageListener:

    def __init__(self, subscription_id: str) -> None:
        self.listeners = {}
        self.subscription_id = subscription_id
        self.subscriber = pubsub_v1.SubscriberClient()
        self.streaming_pull_future = None

    def add_listener(self, tx_id, listener: Listener):
        logger.info(f"Added {tx_id} to listeners on {self.subscription_id}")
        self.listeners[tx_id] = listener

    def remove_listener(self, tx_id):
        if tx_id in self.listeners:
            logger.info(f"Removed {tx_id} to listeners on {self.subscription_id}")
            del self.listeners[tx_id]

    def remove_all(self):
        self.listeners = {}

    def on_message(self, message):
        logger.info(f'Current tx_ids: {self.listeners.keys()}')
        tx_id = message.attributes.get('tx_id')
        logger.info(f"Received tx_id from header {tx_id} on {self.subscription_id}")
        if tx_id in self.listeners:
            message.ack()
            logger.info(f"Acking message with tx_id {tx_id}")
            listener = self.listeners[tx_id]
            listener.set_complete()
            listener.set_message(message)
        else:
            message.ack()
            logger.error(f"NOT EXPECTED! acking message with tx_id {tx_id}")
            logger.error(f"Remaining keys: {self.listeners.keys()}")

    def start(self):
        """
        Begin listening to the pubsub subscription.

        This functions spawns new threads that listen to the subscription topic and
        on receipt of a message invoke the callback function

        The main thread blocks indefinitely unless the connection times out
        """
        self.subscriber = pubsub_v1.SubscriberClient()
        subscription_path = self.subscriber.subscription_path(PROJECT_ID, self.subscription_id)
        self.streaming_pull_future = self.subscriber.subscribe(subscription_path, callback=self.on_message)
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


class QuarantineDatastoreChecker:
    """
    Will poll datastore
    at intervals instead of listening to pubsub for messages.
    """

    def __init__(self):
        # Dictionary containing expected quarantine tx_id:listener
        self.listeners={}
        # Boolean to enable polling of datastore
        self.enabled = False
        # How many times we poll before timing out
        self.max_polls = 4
        # Interval between polls (seconds)
        self.poll_interval = 5

    def add_listener(self, tx_id, listener: Listener):
        """
        Add something for the class to listen for when running
        the start method
        """
        logger.info(f"Added {tx_id} to listeners on quarantineChecker")
        self.listeners[tx_id] = listener

    def remove_listener(self, tx_id):
        """
        Remove a specific tx_id from the listener dictionary
        """
        if tx_id in self.listeners:
            logger.info(f"Removed {tx_id} to listeners on quarantineChecker")
            del self.listeners[tx_id]

    def remove_all(self):
        """
        Remove all the tx_id's from the listener dictionary
        """
        self.listeners = {}

    def on_message(self, message):
        """
        Callback function
        """
        logger.info(f'Current tx_ids: {self.listeners.keys()}')
        tx_id = message.attributes.get('tx_id')
        logger.info(f"Received tx_id from header {tx_id} on {self.subscription_id}")
        if tx_id in self.listeners:
            message.ack()
            logger.info(f"Acking message with tx_id {tx_id}")
            listener = self.listeners[tx_id]
            listener.set_complete()
            listener.set_message(message)
        else:
            message.ack()
            logger.error(f"NOT EXPECTED! acking message with tx_id {tx_id}")
            logger.error(f"Remaining keys: {self.listeners.keys()}")

    def stop(self):
        """
        Stop polling datastore for new
        messages
        """
        self.enabled = False

    def start(self):
        """
        Start checking datastore
        for mew messages
        """
        self.enabled = True
        # Track the number of polls we make
        poll_count = 0
        while self.enabled and poll_count < self.max_polls:
            poll_count += 1
            messages = fetch_quarantined_messages()
            time.sleep(self.poll_interval)



