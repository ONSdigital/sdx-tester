from google.cloud import pubsub_v1

from app.messaging import PROJECT_ID, SURVEY_TOPIC, SEFT_TOPIC, DAP_RECEIPT_TOPIC

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, SURVEY_TOPIC)
seft_topic_path = publisher.topic_path(PROJECT_ID, SEFT_TOPIC)
dap_receipt_topic_path = publisher.topic_path(PROJECT_ID, DAP_RECEIPT_TOPIC)


def publish_data(data: str, tx_id: str) -> None:
    print(f"publishing data with tx_id: {tx_id}")
    # Data must be a bytestring
    data = data.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data, tx_id=tx_id)
    print(future.result())


def publish_seft(message: str, tx_id: str) -> None:
    print(message)
    print(f"publishing seft with tx_id: {tx_id}")
    # Data must be a bytestring
    message = message.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = publisher.publish(seft_topic_path, message, tx_id=tx_id)
    print(future.result())


def publish_dap_receipt(dap_message, tx_id: str) -> None:
    print('Publishing to confirm data is stored by DAP')
    msg_data = dap_message.data
    attributes = {
        'gcs.bucket': dap_message.attributes.get('gcs.bucket'),
        'gcs.key': dap_message.attributes.get('gcs.key'),
        'tx_id': tx_id
    }
    future = publisher.publish(dap_receipt_topic_path, msg_data, **attributes)
    print(future.result())
