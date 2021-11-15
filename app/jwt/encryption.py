import io
import structlog
import zipfile
import yaml

from sdc.crypto.key_store import KeyStore
from sdc.crypto.encrypter import encrypt
from sdc.crypto.decrypter import decrypt as sdc_decrypt
from app.jwt import KEY_PURPOSE_SUBMISSION

logger = structlog.get_logger()


def encrypt_survey(submission: dict, eq_version_3: bool = False) -> str:
    """
    Encrypts survey submission using a public key.

    There are two sets of public and private keys - one pair for encryption and another for signing.

    Encryption is used to ensure only SDX can read a survey response. Signing is used to ensure SDX only trusts encrypted
    responses sent from eQ.
    """
    sdx_key = open("keys/test_sdx-public-jwt.yaml")
    eq_key = open("keys/test_eq-private-signing.yaml")
    eqv3_key = open("keys/test_eqv3-private-signing.yaml")

    if eq_version_3:
        key_store = load_keys(sdx_key, eqv3_key)
    else:
        key_store = load_keys(sdx_key, eq_key)

    payload = encrypt(submission, key_store, 'submission')

    sdx_key.close()
    eq_key.close()
    eqv3_key.close()

    return payload


def decrypt_survey(payload: bytes, eq_version_3: bool = False) -> dict:
    """
    Decrypts an encrypted bytes payload using sdx private key and verifies the signature using the signing public key

    The payload needs to be a JWE encrypted using SDX's public key.
    The JWE ciphertext should represent a JWS signed by EQ using their private key and with the survey json as the claims set.
    """
    sdx_key = open("keys/test_sdx-private-jwt.yaml")
    eq_key = open("keys/test_eq-public-signing.yaml")
    eqv3_key = open("keys/test_eq-public-signing.yaml")

    if eq_version_3:
        key_store = load_keys(sdx_key, eqv3_key)
    else:
        key_store = load_keys(sdx_key, eq_key)

    b_payload = payload.decode('utf-8')
    decrypted_json = sdc_decrypt(b_payload, key_store, KEY_PURPOSE_SUBMISSION)
    sdx_key.close()
    eq_key.close()
    eqv3_key.close()

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
