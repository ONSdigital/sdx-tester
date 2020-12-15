import yaml
from sdc.crypto.key_store import KeyStore
from sdc.crypto.encrypter import encrypt
from sdc.crypto.decrypter import decrypt as sdc_decrypt


KEY_PURPOSE_SUBMISSION = 'submission'


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


