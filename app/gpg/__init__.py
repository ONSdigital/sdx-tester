import gnupg

from app import PROJECT_ID, DATA_RECIPIENT
from app.secret_manager import get_secret

gpg = gnupg.GPG()
encryption_key = get_secret(PROJECT_ID, 'dap-public-gpg')

gpg.import_keys(encryption_key)

RECIPIENTS = [DATA_RECIPIENT]

with open('dap_private_gpg.asc') as f:
    key_data = f.read()
    f.close()
gpg.import_keys(key_data)
