import threading
import time

from app import DAP_SUBSCRIPTION, MAX_WAIT_TIME_SECS, RECEIPT_SUBSCRIPTION, QUARANTINE_SUBSCRIPTION
from app.messaging.publisher import publish_data
from app.messaging.subscriber import MessageListener, Listener
from app.result import Result


class MessageManager:

    def __init__(self) -> None:
        print("starting message manager")
        self.dap_listener = MessageListener(DAP_SUBSCRIPTION)
        self.t = threading.Thread(target=self.dap_listener.start, daemon=True)
        self.t.start()

        self.receipt_listener = MessageListener(RECEIPT_SUBSCRIPTION)
        self.r = threading.Thread(target=self.receipt_listener.start, daemon=True)
        self.r.start()

        self.quarantine_listener = MessageListener(QUARANTINE_SUBSCRIPTION)
        self.q = threading.Thread(target=self.quarantine_listener.start, daemon=True)
        self.q.start()
        print("ready")

    def submit(self, result: Result, data):

        tx_id = result.get_tx_id()
        listener = Listener()
        self.dap_listener.add_listener(tx_id, listener)
        r_listener = Listener()
        self.receipt_listener.add_listener(tx_id, r_listener)
        q_listener = Listener()
        self.quarantine_listener.add_listener(tx_id, q_listener)

        try:
            print("Publishing data", tx_id)
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
                self.remove_listeners(tx_id)
                return result

            if q_listener.is_complete():
                print("Quarantined")
                result.set_quarantine(q_listener.get_message())
                self.remove_listeners(tx_id)
                return result

            if listener.is_complete():
                result.set_dap(listener.get_message())
                dap_completed = True

            if r_listener.is_complete():
                result.set_receipt(r_listener.get_message())
                receipt_completed = True

            if dap_completed and receipt_completed:
                print("completed")
                self.remove_listeners(tx_id)
                return result
            else:
                print("waiting")
                time.sleep(1)
                count += 1

    def remove_listeners(self, tx_id):
        self.dap_listener.remove_listener(tx_id)
        self.receipt_listener.remove_listener(tx_id)
        self.quarantine_listener.remove_listener(tx_id)

    def shut_down(self):
        self.dap_listener.stop()
        self.t.join()
