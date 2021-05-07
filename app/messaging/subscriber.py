import logging
from concurrent.futures import TimeoutError

from google.cloud import pubsub_v1
from app.messaging import PROJECT_ID
from structlog import wrap_logger


logger = wrap_logger(logging.getLogger(__name__))


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
