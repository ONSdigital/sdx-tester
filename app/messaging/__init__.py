from app import PROJECT_ID

# publishing config
SURVEY_TOPIC = "survey-topic"

SEFT_TOPIC = "seft-topic"

# Subscriber config
DAP_SUBSCRIPTION = "dap-subscription"

# Quarantine queue for JSON submissions
SURVEY_QUARANTINE_SUBSCRIPTION = "quarantine-survey-subscription"

# Quarantine queue for SEFT submissions
SEFT_QUARANTINE_SUBSCRIPTION = "quarantine-seft-subscription"

# Subscription to receipt going to RASRM
RECEIPT_SUBSCRIPTION = "receipt-subscription"

# Publishes to topic triggering cleanup cloud function
DAP_RECEIPT_TOPIC = "dap-receipt-topic"

# Time until listener times out listening for a submission
MAX_WAIT_TIME_SECS = 300

from app.messaging.manager import MessageManager, SubmitManager


def get_message_manager(listen: bool = True) -> SubmitManager:
    if listen:
        return MessageManager()
    else:
        return SubmitManager()
