from google.cloud import secretmanager
import structlog

logger = structlog.get_logger()


def get_secret(project_id: str, secret_id: str) -> bytes:
    """
    Makes API call to Google Secret Manager, retrieving secret.
    """
    logger.info("Getting secrets from Secret Manager")
    version_id = 'latest'

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    response = client.access_secret_version(request={"name": name})

    payload = response.payload.data

    return payload
