import logging

from app.gpg import gpg, RECIPIENTS
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def encrypt_seft(data_bytes: bytes) -> str:
    logger.info("Encrypting SEFT")
    encrypted_data = gpg.encrypt(data_bytes, recipients=RECIPIENTS, always_trust=True)

    if encrypted_data.ok:
        logger.info("Successfully encrypted output")
    else:
        logger.error("Failed to encrypt output", status=encrypted_data.status)

    return str(encrypted_data)
