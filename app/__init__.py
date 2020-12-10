from google.cloud import pubsub_v1
from flask import Flask

app = Flask(__name__)

from app import routes

project_id = "ons-sdx-sandbox"
dap_topic_id = "dap-topic"
receipt_topic_id = "receipt-topic"

# Subscriber setup
subscription_id = "survey-subscription"

survey_subscriber = pubsub_v1.SubscriberClient()
# The `subscription_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/subscriptions/{subscription_id}`
subscription_path = survey_subscriber.subscription_path(project_id, subscription_id)



