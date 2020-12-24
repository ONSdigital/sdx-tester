import logging
import os

from google.cloud import pubsub_v1
from flask import Flask

LOGGING_LEVEL = logging.getLevelName(os.getenv('LOGGING_LEVEL', 'INFO'))
LOGGING_FORMAT = "%(asctime)s.%(msecs)06dZ|%(levelname)s: sdx-worker: %(message)s"

logging.basicConfig(
    format=LOGGING_FORMAT,
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=LOGGING_LEVEL,
)

project_id = "ons-sdx-sandbox"

# publishing config
topic_id = "survey-topic"

publisher = pubsub_v1.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
topic_path = publisher.topic_path(project_id, topic_id)


# Subscriber config
dap_subscription_id = "dap-subscription"

survey_subscriber = pubsub_v1.SubscriberClient()
# The `subscription_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/subscriptions/{subscription_id}`
dap_subscription_path = survey_subscriber.subscription_path(project_id, dap_subscription_id)

app = Flask(__name__)
from app import routes
