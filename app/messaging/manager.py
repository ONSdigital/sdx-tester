import threading
import time
import structlog

from app.messaging import DAP_SUBSCRIPTION, MAX_WAIT_TIME_SECS, RECEIPT_SUBSCRIPTION, SEFT_QUARANTINE_SUBSCRIPTION
from app.messaging.publisher import publish_data, publish_seft
from app.messaging.subscriber import PubsubListener, Target, DatastoreListener
from app.result import Result


logger = structlog.get_logger()


class SubmitManager:

    def start(self):
        pass

    def stop(self):
        pass

    def submit(self, result: Result, data: str, is_seft: bool = False, requires_receipt: bool = False, requires_publish: bool = True):
        tx_id = result.get_tx_id()
        logger.info(f"requires receipt: {requires_receipt}")
        logger.info("Publishing data", tx_id=tx_id)
        if is_seft:
            publish_seft(data, tx_id)
        else:
            publish_data(data, tx_id)
        return result


class MessageManager(SubmitManager):

    """
    This class provides a common interface for different types of listeners to publish either JSON submission or seft metadata
    to PubSub Topic: "survey-topic" and "seft-topic" respectively
    """

    def __init__(self) -> None:
        self.dap_listener = PubsubListener(DAP_SUBSCRIPTION)
        self.t = None

        self.receipt_listener = PubsubListener(RECEIPT_SUBSCRIPTION)
        self.r = None

        self.quarantine_listener = DatastoreListener()
        self.q = None

        self.seft_quarantine_listener = PubsubListener(SEFT_QUARANTINE_SUBSCRIPTION)
        self.sq = None

    def start(self):
        logger.info("Starting Message Manager")

        self.t = threading.Thread(target=self.dap_listener.start, daemon=True)
        self.r = threading.Thread(target=self.receipt_listener.start, daemon=True)
        self.q = threading.Thread(target=self.quarantine_listener.start, daemon=True)
        self.sq = threading.Thread(target=self.seft_quarantine_listener.start, daemon=True)

        self.t.start()
        self.r.start()
        self.q.start()
        self.sq.start()

        logger.info("Ready")

    def submit(self,
               result: Result,
               data: str,
               is_seft: bool = False,
               requires_receipt: bool = False,
               requires_publish: bool = False):

        logger.info("Calling submit")
        tx_id = result.get_tx_id()
        dap_target = Target()
        self.dap_listener.add_target(tx_id, dap_target)

        receipt_target = Target()
        if requires_receipt:
            self.receipt_listener.add_target(tx_id, receipt_target)
        else:
            receipt_target.set_complete()

        quarantine_target = Target()
        if is_seft:
            self.seft_quarantine_listener.add_target(tx_id, quarantine_target)
        else:
            self.quarantine_listener.add_target(tx_id, quarantine_target)

        try:
            if requires_publish:
                logger.info("Publishing data", tx_id=tx_id)
                if is_seft:
                    publish_seft(data, tx_id)
                else:
                    publish_data(data, tx_id)

        except Exception as e:
            logger.error(e)
            result.record_error(e)
            return result

        count = 0
        dap_completed = False
        receipt_completed = False
        listening = True
        while listening:
            if count > MAX_WAIT_TIME_SECS:
                logger.error("Timed out")
                result.set_timeout(True)
                self._remove_listeners(tx_id)
                return result

            if quarantine_target.is_complete():
                logger.error("Quarantined")
                result.set_quarantine(quarantine_target.get_message())
                self._remove_listeners(tx_id)
                return result

            if dap_target.is_complete():
                result.set_dap(dap_target.get_message())
                dap_completed = True

            if receipt_target.is_complete():
                result.set_receipt(receipt_target.get_message())
                receipt_completed = True

            if dap_completed and receipt_completed:
                logger.info("Completed")
                self._remove_listeners(tx_id)
                return result
            else:
                logger.info("Waiting")
                time.sleep(1)
                count += 1

    def _remove_listeners(self, tx_id):
        logger.info("Removing listeners")
        self.dap_listener.remove_target(tx_id)
        self.receipt_listener.remove_target(tx_id)
        self.quarantine_listener.remove_target(tx_id)
        self.seft_quarantine_listener.remove_target(tx_id)

    def stop(self):
        logger.info("Stopping Message Manager")
        self.dap_listener.remove_all()
        self.dap_listener.stop()
        self.t.join()

        self.receipt_listener.remove_all()
        self.receipt_listener.stop()
        self.r.join()

        self.quarantine_listener.remove_all()
        self.quarantine_listener.stop()
        self.q.join()

        self.seft_quarantine_listener.remove_all()
        self.seft_quarantine_listener.stop()
        self.sq.join()
