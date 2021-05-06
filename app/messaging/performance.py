import logging
import threading
import time

from app.messaging import DAP_SUBSCRIPTION, RECEIPT_SUBSCRIPTION
from app.messaging.subscriber import MessageListener
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))

# Time until listener times out listening for a submission
MAX_WAIT_TIME_SECS = 300


class PerformanceListener(MessageListener):

    def __init__(self, subscription_id: str):
        super().__init__(subscription_id)
        self.message_count = 0

    def on_message(self, message):
        tx_id = message.attributes.get('tx_id')
        logger.info(f"Received tx_id from header {tx_id} on {self.subscription_id}")
        message.ack()
        self.message_count += 1
        logger.info(f'Received count = {self.message_count}')


class ReceiptListener(MessageListener):

    def on_message(self, message):
        message.ack()


class PerformanceManager:

    def __init__(self):
        self.listener = PerformanceListener(DAP_SUBSCRIPTION)
        self.t = threading.Thread(target=self.listener.start, daemon=True)

        self.receipt_listener = ReceiptListener(RECEIPT_SUBSCRIPTION)
        self.r = threading.Thread(target=self.receipt_listener.start, daemon=True)

    def start(self, total: int) -> tuple:
        logger.info("Starting Performance Manager")
        self.t.start()
        self.r.start()

        listening = True
        time_in_secs = 0
        while listening:

            if self.listener.message_count >= total:
                listening = False

            elif time_in_secs > MAX_WAIT_TIME_SECS:
                logger.error("Timed out")
                listening = False

            else:
                time.sleep(1)
                time_in_secs += 1

        return self.listener.message_count, time_in_secs

    def stop(self):
        logger.info("Stopping Performance Manager")
        self.listener.stop()
        self.t.join()

        self.receipt_listener.stop()
        self.r.join()
