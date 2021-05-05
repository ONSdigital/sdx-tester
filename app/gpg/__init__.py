import gnupg

from app import PROJECT_ID
from app.secret_manager import get_secret

gpg = gnupg.GPG()
encryption_key = get_secret(PROJECT_ID, 'dap-public-gpg')

if PROJECT_ID == "ons-sdx-preprod":
    recipients = ["sdx_preprod@ons.gov.uk"]
else:
    recipients = ['dap@ons.gov.uk']

gpg.import_keys(encryption_key)

RECIPIENTS = recipients

with open('dap_private_gpg.asc') as f:
    key_data = f.read()
    f.close()
gpg.import_keys(key_data)
