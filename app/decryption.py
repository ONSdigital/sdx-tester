import logging
from structlog import wrap_logger

from app import gpg

logger = wrap_logger(logging.getLogger(__name__))


def decrypt_survey(data_bytes: bytes) -> str:

    decrypted_data = gpg.decrypt_file(data_bytes, passphrase='passphrase')

    if decrypted_data.ok:
        logger.info("successfully decrypted output")
    else:
        logger.info("failed to decrypt output")
        logger.info(decrypted_data.status)

    return str(decrypted_data)
