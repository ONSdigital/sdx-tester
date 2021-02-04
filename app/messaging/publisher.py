from google.cloud import pubsub_v1

from app import PROJECT_ID
from app.messaging import SURVEY_TOPIC, SEFT_TOPIC

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, SURVEY_TOPIC)
seft_topic_path = publisher.topic_path(PROJECT_ID, SEFT_TOPIC)


def publish_data(data: str, tx_id: str) -> None:
    # Data must be a bytestring
    data = data.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data, tx_id=tx_id)
    print(future.result())


def publish_seft(message: str, tx_id: str) -> None:
    # Data must be a bytestring
    message = message.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = publisher.publish(seft_topic_path, message, tx_id=tx_id)
    print(future.result())
