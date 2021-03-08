import logging
from google.cloud import pubsub_v1

from app.messaging import PROJECT_ID, SURVEY_TOPIC, SEFT_TOPIC
from structlog import wrap_logger

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, SURVEY_TOPIC)
seft_topic_path = publisher.topic_path(PROJECT_ID, SEFT_TOPIC)
logger = wrap_logger(logging.getLogger(__name__))

def publish_data(data: str, tx_id: str) -> None:
    logger.info(f"Publishing data with tx_id: {tx_id}")
    # Data must be a bytestring
    data = data.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data, tx_id=tx_id)
    logger.info(future.result())


def publish_seft(message: str, tx_id: str) -> None:
    logger.info(f"Publishing seft with tx_id: {tx_id}")
    # Data must be a bytestring
    message = message.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = publisher.publish(seft_topic_path, message, tx_id=tx_id)
    logger.info(future.result())
