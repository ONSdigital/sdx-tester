import os
import unittest
import glob
import pandas

from comment_tests import surveys
from comment_tests.helper_functions import bucket_cleanup, create_comments, wait_for_comments, extract_files, \
    clean_datastore, run_job


class TestComments(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        clean_datastore()
        bucket_cleanup()
        create_comments()
        run_job()
        # wait_for_comments()
        extract_files()

    @classmethod
    def tearDownClass(cls):
        files = glob.glob('temp_files/*.xlsx')
        for f in files:
            os.remove(f)

    def test_all(self):
        for x in surveys:
            with self.subTest(msg=f'Testing survey: {x}', survey=x):
                result = pandas.read_excel(f'temp_files/{x}_201605.xlsx', header=None)
                self.assertEqual(result.iat[2, 3], f'I am a {x} comment')
                self.assertEqual(int(result.iat[2, 1]), 201605)

    def test_create_zip_verify_134(self):
        result = pandas.read_excel('temp_files/134_201605.xlsx', header=None)

        self.assertEqual(result.iat[2, 2], '91w, 95w, 96w, 97w, 91f, 95f, 96f, 97f, 191m, 195m, 196m, 197m, 191w4, '
                                           '195w4, 196w4, 197w4, 191w5, 195w5, 196w5, 197w5, ')
        self.assertEqual(result.iat[2, 3], 'flux clean')
        self.assertEqual(result.iat[2, 4], 'Pipe mania')
        self.assertEqual(result.iat[2, 5], 'Gas leak')
        self.assertEqual(result.iat[2, 6], 'copper pipe')
        self.assertEqual(result.iat[2, 7], 'solder joint')
        self.assertEqual(result.iat[2, 8], 'drill hole')
        self.assertEqual(int(result.iat[2, 1]), 201605)
