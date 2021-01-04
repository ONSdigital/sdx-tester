from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1

from app import PROJECT_ID


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
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(PROJECT_ID, subscription_id)
        self.streaming_pull_future = self.subscriber.subscribe(self.subscription_path, callback=self.on_message)

    def add_listener(self, tx_id, listener: Listener):
        self.listeners[tx_id] = listener

    def remove_listener(self, tx_id):
        del self.listeners[tx_id]

    def on_message(self, message):
        tx_id = message.attributes.get('tx_id')
        print(f"received tx_id from header {tx_id} on {self.subscription_path}")
        if tx_id in self.listeners.keys():
            message.ack()
            print(f"acking message with tx_id {tx_id}")
            listener = self.listeners[tx_id]
            listener.set_complete()
            listener.set_message(message)
        else:
            message.ack()
            print(f"nacking message with tx_id {tx_id}")
            print(f"remaining keys: {self.listeners.keys()}")

    def start(self):
        print(f"Listening for messages on {self.subscription_path}..\n")

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
