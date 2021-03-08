import logging
import threading
import time

from app.messaging import DAP_SUBSCRIPTION, MAX_WAIT_TIME_SECS, RECEIPT_SUBSCRIPTION, SURVEY_QUARANTINE_SUBSCRIPTION, \
    SEFT_QUARANTINE_SUBSCRIPTION
from app.messaging.publisher import publish_data, publish_seft
from app.messaging.subscriber import MessageListener, Listener
from app.result import Result

logger = logging.getLogger(__name__)


class MessageManager:

    def __init__(self) -> None:
        self.dap_listener = MessageListener(DAP_SUBSCRIPTION)
        self.t = None

        self.receipt_listener = MessageListener(RECEIPT_SUBSCRIPTION)
        self.r = None

        self.quarantine_listener = MessageListener(SURVEY_QUARANTINE_SUBSCRIPTION)
        self.q = None

        self.seft_quarantine_listener = MessageListener(SEFT_QUARANTINE_SUBSCRIPTION)
        self.sq = None

    def start(self):
        print("starting message manager")

        self.t = threading.Thread(target=self.dap_listener.start, daemon=True)
        self.r = threading.Thread(target=self.receipt_listener.start, daemon=True)
        self.q = threading.Thread(target=self.quarantine_listener.start, daemon=True)
        self.sq = threading.Thread(target=self.seft_quarantine_listener.start, daemon=True)

        self.t.start()
        self.r.start()
        self.q.start()
        self.sq.start()

        print("ready")

    def submit(self, result: Result, data: str, is_seft: bool = False):
        print("calling submit")
        tx_id = result.get_tx_id()
        listener = Listener()
        self.dap_listener.add_listener(tx_id, listener)

        r_listener = Listener()
        if is_seft:
            # SEFTs don't require a receipt
            r_listener.set_complete()
        else:
            self.receipt_listener.add_listener(tx_id, r_listener)

        q_listener = Listener()
        if is_seft:
            self.seft_quarantine_listener.add_listener(tx_id, q_listener)
        else:
            self.quarantine_listener.add_listener(tx_id, q_listener)

        try:
            print("Publishing data", tx_id)
            if is_seft:
                publish_seft(data, tx_id)
            else:
                publish_data(data, tx_id)
        except Exception as e:
            print(e)
            result.record_error(e)
            return result

        count = 0
        dap_completed = False
        receipt_completed = False
        listening = True
        while listening:
            if count > MAX_WAIT_TIME_SECS:
                print("Timed out")
                result.set_timeout(True)
                self._remove_listeners(tx_id)
                return result

            if q_listener.is_complete():
                print("Quarantined")
                result.set_quarantine(q_listener.get_message())
                self._remove_listeners(tx_id)
                return result

            if listener.is_complete():
                result.set_dap(listener.get_message())
                dap_completed = True

            if r_listener.is_complete():
                result.set_receipt(r_listener.get_message())
                receipt_completed = True

            if dap_completed and receipt_completed:
                print("completed")
                self._remove_listeners(tx_id)
                return result
            else:
                print("waiting")
                time.sleep(1)
                count += 1

    def _remove_listeners(self, tx_id):
        print("removing listeners")
        self.dap_listener.remove_listener(tx_id)
        self.receipt_listener.remove_listener(tx_id)
        self.quarantine_listener.remove_listener(tx_id)
        self.seft_quarantine_listener.remove_listener(tx_id)

    def stop(self):
        print("stopping message manager")
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
