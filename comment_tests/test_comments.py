import io
import os
import unittest
import zipfile
import glob
import pandas
import time
from datetime import datetime, date
from app.store.reader import get_comment_files, check_file_exists

d = date.today()
FILE_PATH = f'comments/{datetime(d.year, d.month, d.day).date()}.zip'
TIMEOUT = 120


class TestComments(unittest.TestCase):
    """
    This test should be run from the concourse pipeline.
    If you want to run it locally, ensure you have triggered the sdx-collate cronjob after running test_setup.py
    This can be achieve by running: kubectl create job --from=cronjob/sdx-collate test-collate.
    """

    surveys = ['009',
               '017',
               '019',
               '023',
               '139',
               '144',
               '147',
               '160',
               '165',
               '182',
               '183',
               '184',
               '185',
               '187',
               '228',
               '283']

    @classmethod
    def setUpClass(cls):
        count = 0
        while not check_file_exists(FILE_PATH) or count > TIMEOUT:
            print('SDX-Collate waiting for resources. Waiting 20 seconds...')
            time.sleep(10)
            count += 10
        result = get_comment_files(FILE_PATH)
        z = zipfile.ZipFile(io.BytesIO(result), "r")
        z.extractall('temp_files')

    @classmethod
    def tearDownClass(cls):
        files = glob.glob('temp_files/*.xls')
        for f in files:
            os.remove(f)

    def test_all(self):
        for x in self.surveys:
            with self.subTest(msg=f'Testing survey: {x}', survey=x):
                result = pandas.read_excel(f'temp_files/{x}_201605.xls')
                self.assertEqual(result.iat[1, 3], f'I am a {x} comment')
                self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_create_zip_verify_134(self):
        result = pandas.read_excel('temp_files/134_201605.xls')

        self.assertEqual(result.iat[1, 2], '91w, 95w, 96w, 97w, 91f, 95f, 96f, 97f, 191m, 195m, 196m, 197m, 191w4, '
                                           '195w4, 196w4, 197w4, 191w5, 195w5, 196w5, 197w5, ')
        self.assertEqual(result.iat[1, 3], 'flux clean')
        self.assertEqual(result.iat[1, 4], 'Pipe mania')
        self.assertEqual(result.iat[1, 5], 'Gas leak')
        self.assertEqual(result.iat[1, 6], 'copper pipe')
        self.assertEqual(result.iat[1, 7], 'solder joint')
        self.assertEqual(result.iat[1, 8], 'drill hole')
        self.assertEqual(int(result.iat[1, 1]), 201605)
