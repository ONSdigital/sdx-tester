from app import PROJECT_ID

# publishing config
SURVEY_TOPIC = "survey-topic"

SEFT_TOPIC = "seft-topic"

# Subscriber config
DAP_SUBSCRIPTION = "dap-subscription"

SURVEY_QUARANTINE_SUBSCRIPTION = "quarantine-survey-subscription"

SEFT_QUARANTINE_SUBSCRIPTION = "quarantine-seft-subscription"

RECEIPT_SUBSCRIPTION = "receipt-subscription"

DAP_RECEIPT_TOPIC = "dap-receipt-topic"

MAX_WAIT_TIME_SECS = 30


from app.messaging.manager import MessageManager, SubmitManager


def get_message_manager(listen: bool = True) -> SubmitManager:
    if listen:
        return MessageManager()
    else:
        return SubmitManager()
