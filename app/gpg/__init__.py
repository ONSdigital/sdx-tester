import gnupg

DAP_RECIPIENT = 'dap@ons.gov.uk'

gpg = gnupg.GPG()

with open('dap_private_key.asc') as f:
    key_data = f.read()
    f.close()
gpg.import_keys(key_data)
