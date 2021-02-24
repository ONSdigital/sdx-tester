import json

from cryptography.fernet import Fernet

COMMENT_KEY = "E3rjFT2i9ALcvc99Pe3YqjIGrzm3LdMsCXc8nUaOEbc="


def encrypt_comment(data: dict) -> str:
    comment_str = json.dumps(data)
    f = Fernet(COMMENT_KEY)
    token = f.encrypt(comment_str.encode())
    return token.decode()
