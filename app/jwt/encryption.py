import io
import logging
import zipfile
import yaml
from sdc.crypto.key_store import KeyStore
from sdc.crypto.encrypter import encrypt
from sdc.crypto.decrypter import decrypt as sdc_decrypt
from structlog import wrap_logger

from app.jwt import KEY_PURPOSE_SUBMISSION

logger = wrap_logger(logging.getLogger(__name__))


def encrypt_survey(submission: dict) -> str:
    logger.info("Encrypting survey")
    with open("./keys.yml") as file:
        secrets_from_file = yaml.safe_load(file)
    key_store = KeyStore(secrets_from_file)
    payload = encrypt(submission, key_store, 'submission')
    return payload


def decrypt_survey(payload: bytes) -> dict:
    logger.info("Decrypting survey")
    with open("./keys2.yml") as file2:
        secrets_from_file2 = yaml.safe_load(file2)
    key_store2 = KeyStore(secrets_from_file2)
    b_payload = payload.decode('utf-8')
    decrypted_json = sdc_decrypt(b_payload, key_store2, KEY_PURPOSE_SUBMISSION)
    return decrypted_json


def view_zip_content(zip_file: str):
    z = zipfile.ZipFile(io.BytesIO(zip_file), "r")
    print(z.printdir())
    return True
