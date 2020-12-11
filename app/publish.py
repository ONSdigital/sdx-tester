from app import publisher, topic_path


def publish_data(data, tx_id):
    # Data must be a bytestring
    data = data.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data, tx_id=tx_id)
    return future.result()

