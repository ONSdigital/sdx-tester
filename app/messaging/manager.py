import threading
import time
from enum import Enum

from app import DAP_SUBSCRIPTION, MAX_WAIT_TIME_SECS
from app.messaging.publisher import publish_data
from app.messaging.subscriber import MessageListener, Listener


class MessageState(Enum):
    SENT = 1
    FAILED_SEND = 2
    RECEIVED_DAP = 3
    RECEIVED_RECEIPT = 4
    QUARANTINED = 5
    TIMED_OUT = 6


class MessageManager:

    def __init__(self) -> None:
        print("starting message manager")
        self.dap_listener = MessageListener(DAP_SUBSCRIPTION)
        self.t = threading.Thread(target=self.dap_listener.start, daemon=True)
        self.t.start()
        print("ready")

    def submit(self, tx_id, data):
        result = []

        listener = Listener()
        self.dap_listener.add_listener(tx_id, listener)

        print("Publishing data", tx_id)
        published = publish_data(data, tx_id)
        if published:
            result.append(MessageState.SENT)
        else:
            result.append(MessageState.FAILED_SEND)
            return result

        count = 0
        while not listener.is_complete():
            if count > MAX_WAIT_TIME_SECS:
                print("Timed out")
                result.append(MessageState.TIMED_OUT)
                return result
            print("waiting")
            time.sleep(1)
            count += 1

        result.append(MessageState.RECEIVED_DAP)
        return result

    def shut_down(self):
        self.dap_listener.stop()
        self.t.join()
