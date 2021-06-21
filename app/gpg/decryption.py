import os
import structlog

from app.gpg import gpg

logger = structlog.get_logger()


def decrypt_output(data: bytes, filename: str) -> bytes:

    # we seem to have to write the decrypted data out to a file
    temp_file = f'temp_files/{filename}'
    decrypted_data = gpg.decrypt(data, passphrase='passphrase', output=temp_file)

    if decrypted_data.ok:
        logger.info("Successfully decrypted output")

        # read the data back in from the created file
        with open(temp_file, 'rb') as f:
            result_bytes = f.read()

        # delete the file as it is no longer needed
        os.remove(temp_file)

    else:
        logger.error("Failed to decrypt output", status=decrypted_data.status)
        raise

    return result_bytes
