import logging

from app.gpg import gpg, DAP_RECIPIENT
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def encrypt_seft(data_bytes: bytes) -> str:
    """
    Seft output is encrypted using a public GPG key and then it is placed in the ons-sdx-{{project_id}}-seft-responses GCP bucket.
    """
    logger.info("Encrypting SEFT")
    encrypted_data = gpg.encrypt(data_bytes, recipients=[DAP_RECIPIENT], always_trust=True)

    if encrypted_data.ok:
        logger.info("Successfully encrypted output")
    else:
        logger.error("Failed to encrypt output", status=encrypted_data.status)

    return str(encrypted_data)
