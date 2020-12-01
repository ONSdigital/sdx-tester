# from google.cloud import pubsub_v1
#
#
# project_id = "ons-sdx-sandbox"
# topic_id = "test"
#
# publisher = pubsub_v1.PublisherClient()
# # The `topic_path` method creates a fully qualified identifier
# # in the form `projects/{project_id}/topics/{topic_id}`
# topic_path = publisher.topic_path(project_id, topic_id)
#
#
# def publish_data(data):
#     # Data must be a bytestring
#     data = data.encode("utf-8")
#     # When you publish a message, the client returns a future.
#     future = publisher.publish(topic_path, data)
#     return future.result()
