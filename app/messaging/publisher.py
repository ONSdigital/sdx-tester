from google.cloud import pubsub_v1

from app import PROJECT_ID, SURVEY_TOPIC

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, SURVEY_TOPIC)


def publish_data(data: str, tx_id: str) -> bool:
    try:
        # Data must be a bytestring
        data = data.encode("utf-8")
        # When you publish a message, the client returns a future.
        future = publisher.publish(topic_path, data, tx_id=tx_id)
        print(future.result())
    except Exception as e:
        print(e)
        return False
    return True

