from app.gpg import gpg, DAP_RECIPIENT


def encrypt_seft(data_bytes: bytes) -> str:

    encrypted_data = gpg.encrypt(data_bytes, recipients=[DAP_RECIPIENT], always_trust=True)

    if encrypted_data.ok:
        print("successfully encrypted output")
    else:
        print("failed to encrypt output")
        print(encrypted_data.status)

    return str(encrypted_data)
