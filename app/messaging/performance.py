import logging
import threading
import time

from app.messaging import DAP_SUBSCRIPTION
from app.messaging.subscriber import MessageListener

logger = logging.getLogger(__name__)

MAX_WAIT_TIME_SECS = 300


class PerformanceListener(MessageListener):

    def __init__(self, subscription_id: str):
        super().__init__(subscription_id)
        self.message_count = 0

    def on_message(self, message):
        tx_id = message.attributes.get('tx_id')
        logger.info(f"received tx_id from header {tx_id} on {self.subscription_id}")
        message.ack()
        self.message_count += 1
        print(f'received count = {self.message_count}')


class PerformanceManager:

    def __init__(self):
        self.listener = PerformanceListener(DAP_SUBSCRIPTION)
        self.t = threading.Thread(target=self.listener.start, daemon=True)

    def start(self, total: int) -> tuple:
        print("starting performance manager")
        self.t.start()

        listening = True
        time_in_secs = 0
        while listening:

            if self.listener.message_count == total:
                listening = False

            elif time_in_secs > MAX_WAIT_TIME_SECS:
                print("Timed out")
                listening = False

            else:
                time.sleep(1)
                time_in_secs += 1

        return self.listener.message_count, time_in_secs

    def stop(self):
        print("stopping performance manager")
        self.listener.stop()
        self.t.join()