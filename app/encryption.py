import base64
import io
import logging
import zipfile
import yaml
from sdc.crypto.key_store import KeyStore
from sdc.crypto.encrypter import encrypt
from sdc.crypto.decrypter import decrypt as sdc_decrypt
from structlog import wrap_logger

KEY_PURPOSE_SUBMISSION = 'submission'

logger = wrap_logger(logging.getLogger(__name__))


def encrypt_survey(submission: dict) -> str:
    with open("./keys.yml") as file:
        secrets_from_file = yaml.safe_load(file)
    key_store = KeyStore(secrets_from_file)
    payload = encrypt(submission, key_store, 'submission')
    return payload


def decrypt_survey(payload: str) -> dict:
    with open("./keys2.yml") as file2:
        secrets_from_file2 = yaml.safe_load(file2)
    key_store2 = KeyStore(secrets_from_file2)
    decrypted_json = sdc_decrypt(payload, key_store2, KEY_PURPOSE_SUBMISSION)
    return decrypted_json


def view_zip_content(zip_file: str):
    z = zipfile.ZipFile(io.BytesIO(zip_file), "r")
    print(z.printdir())
    return True


def test_decrypt():
    with open('app/Data/my-jwe') as data:
        data_decrypted = decrypt_survey(data.read())
        decoded = base64.b64decode(data_decrypted['zip'])
        view_zip_content(decoded)

test_decrypt()

