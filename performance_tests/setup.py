import unittest

from app.gpg.encryption import encrypt_seft
from app.store.writer import write_seft

SEFT_DIR = "app/Data/sefts"
SEFT_FILENAME = f"11110000014H_202009_057_20210121143526"
SEFT_COUNT = 500


class SetupPerformance(unittest.TestCase):

    def test_prepare_sefts(self):

        with open(f"{SEFT_DIR}/{SEFT_FILENAME}.xlsx", 'rb') as seft_file:
            data_bytes = seft_file.read()

        for i in range(SEFT_COUNT):
            name = f'{SEFT_FILENAME}_{i}'
            encrypted_seft = encrypt_seft(data_bytes)
            write_seft(encrypted_seft, name)
