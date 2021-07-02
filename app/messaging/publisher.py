import json

import structlog

from google.cloud import pubsub_v1
from app.messaging import PROJECT_ID, SURVEY_TOPIC, SEFT_TOPIC, DAP_RECEIPT_TOPIC

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, SURVEY_TOPIC)
seft_topic_path = publisher.topic_path(PROJECT_ID, SEFT_TOPIC)
dap_receipt_topic_path = publisher.topic_path(PROJECT_ID, DAP_RECEIPT_TOPIC)

logger = structlog.get_logger()


def publish_data(data: str, tx_id: str) -> None:
    """
    Publishes JSON submission to PubSub Topic: "survey-topic"
    """
    logger.info(f"Publishing data with tx_id: {tx_id}")
    # Data must be a bytestring
    data = data.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data, tx_id=tx_id)
    logger.info(future.result())


def publish_seft(message: str, tx_id: str) -> None:
    """
    Publishes seft metadata onto seft PubSub Topic: "seft-topic"
    """
    logger.info(f"Publishing seft with tx_id: {tx_id}")
    # Data must be a bytestring
    message = message.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = publisher.publish(seft_topic_path, message, tx_id=tx_id)
    logger.info(future.result())


def publish_dap_receipt(dap_message) -> None:
    """
    Publishes dap receipt to PubSub Topic: "dap-receipt-topic". Kicking off the cleanup function
    """
    logger.info('Publishing to dap-receipt-topic')

    message_str = json.dumps(dap_message)

    b_message = message_str.encode('utf-8')

    future = publisher.publish(dap_receipt_topic_path, b_message)
    logger.info(future.result())
