import os
import unittest
import glob
from datetime import date, timedelta

import pandas

from comment_tests.helper_functions import bucket_cleanup, wait_for_comments, extract_files, \
    clean_datastore, insert_comments, get_datetime


def yesterday() -> date:
    return date.today() - timedelta(1)


class TestDailyComments(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        clean_datastore()
        bucket_cleanup()

        # within 1 day
        insert_comments(['009', '017', '228'], '2201', get_datetime(1))
        insert_comments(['009', '017'], '2202', get_datetime(1))
        insert_comments(['009'], '2203', get_datetime(1))

        # older than 1 day
        insert_comments(['009', '017'], '2201', get_datetime(2))
        insert_comments(['009'], '2201', get_datetime(3))

        os.system('kubectl create job --from=cronjob/sdx-collate test-daily')
        wait_for_comments()
        extract_files()

    def test_009(self):
        print("testing")

    @classmethod
    def tearDownClass(cls):
        files = glob.glob('temp_files/*.xlsx')
        for f in files:
            os.remove(f)
        os.system('kubectl delete job test-daily')

    def test_009(self):
        result = pandas.read_excel(f'temp_files/009_daily_{yesterday()}.xlsx', header=None)
        self.assertEqual(int(result.iat[2, 1]), 2201)
        self.assertEqual(result.iat[2, 3], f'I am a 009 comment')
        self.assertEqual(int(result.iat[3, 1]), 2202)
        self.assertEqual(result.iat[3, 3], f'I am a 009 comment')
        self.assertEqual(int(result.iat[4, 1]), 2203)
        self.assertEqual(result.iat[4, 3], f'I am a 009 comment')

    def test_017(self):
        result = pandas.read_excel(f'temp_files/017_daily_{yesterday()}.xlsx', header=None)
        self.assertEqual(int(result.iat[2, 1]), 2201)
        self.assertEqual(result.iat[2, 3], f'I am a 017 comment')
        self.assertEqual(int(result.iat[3, 1]), 2202)
        self.assertEqual(result.iat[3, 3], f'I am a 017 comment')

    def test_228(self):
        result = pandas.read_excel(f'temp_files/228_daily_{yesterday()}.xlsx', header=None)
        self.assertEqual(int(result.iat[2, 1]), 2201)
        self.assertEqual(result.iat[2, 3], f'I am a 228 comment')
