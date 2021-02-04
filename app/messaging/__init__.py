from app.messaging.manager import MessageManager

# publishing config
SURVEY_TOPIC = "survey-topic"

SEFT_TOPIC = "seft-topic"

# Subscriber config
DAP_SUBSCRIPTION = "dap-subscription"

QUARANTINE_SUBSCRIPTION = "quarantine-subscription"

SEFT_QUARANTINE_SUBSCRIPTION = "seft_quarantine-subscription"

RECEIPT_SUBSCRIPTION = "receipt-subscription"

MAX_WAIT_TIME_SECS = 30


message_manager = MessageManager()
