import io
import os
import unittest
import zipfile
import glob
import pandas
import time

from datetime import date
from app.store.reader import get_comment_files, does_comment_exist
from comment_tests import surveys
from comment_tests.helper_functions import bucket_cleanup, insert_comments
from app.store.reader import cleanup_datastore

TIMEOUT = 150
d = date.today()


class TestComments(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cleanup_datastore()
        bucket_cleanup()
        insert_comments()
        os.system('kubectl create job --from=cronjob/sdx-collate test-collate')
        wait_for_comments()
        result = get_comment_files()
        z = zipfile.ZipFile(io.BytesIO(result), "r")
        z.extractall('temp_files')

    @classmethod
    def tearDownClass(cls):
        files = glob.glob('temp_files/*.xlsx')
        for f in files:
            os.remove(f)
        os.system('kubectl delete job test-collate')

    def test_all(self):
        for x in surveys:
            with self.subTest(msg=f'Testing survey: {x}', survey=x):
                result = pandas.read_excel(f'temp_files/{x}_201605.xlsx')
                self.assertEqual(result.iat[1, 3], f'I am a {x} comment')
                self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_create_zip_verify_134(self):
        result = pandas.read_excel('temp_files/134_201605.xlsx')

        self.assertEqual(result.iat[1, 2], '91w, 95w, 96w, 97w, 91f, 95f, 96f, 97f, 191m, 195m, 196m, 197m, 191w4, '
                                           '195w4, 196w4, 197w4, 191w5, 195w5, 196w5, 197w5, ')
        self.assertEqual(result.iat[1, 3], 'flux clean')
        self.assertEqual(result.iat[1, 4], 'Pipe mania')
        self.assertEqual(result.iat[1, 5], 'Gas leak')
        self.assertEqual(result.iat[1, 6], 'copper pipe')
        self.assertEqual(result.iat[1, 7], 'solder joint')
        self.assertEqual(result.iat[1, 8], 'drill hole')
        self.assertEqual(int(result.iat[1, 1]), 201605)


def wait_for_comments():
    count = 0
    while not does_comment_exist() and count < TIMEOUT:
        print('SDX-Collate waiting for resources. Waiting 20 seconds...')
        time.sleep(20)
        count += 20
