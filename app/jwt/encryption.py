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
    key1 = open("test_sdx-public-jwt.yaml")
    key2 = open("test_eq-private-signing.yaml")
    key_store = load_keys(key1, key2)
    payload = encrypt(submission, key_store, 'submission')
    key1.close()
    key2.close()
    return payload


def decrypt_survey(payload: bytes) -> dict:
    key1 = open("test_sdx-private-jwt.yaml")
    key2 = open("test_eq-public-signing.yaml")
    key_store = load_keys(key1, key2)
    b_payload = payload.decode('utf-8')
    decrypted_json = sdc_decrypt(b_payload, key_store, KEY_PURPOSE_SUBMISSION)
    key1.close()
    key2.close()
    return decrypted_json


def load_keys(*keys) -> KeyStore:
    key_dict = {}
    for k in keys:
        key = yaml.safe_load(k)
        key_dict[key['keyid']] = key
    return KeyStore({"keys": key_dict})


def view_zip_content(zip_file: str):
    z = zipfile.ZipFile(io.BytesIO(zip_file), "r")
    print(z.printdir())
    return True
