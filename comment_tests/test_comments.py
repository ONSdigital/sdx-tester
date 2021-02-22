import io
import os
import unittest
import zipfile
import glob
from datetime import datetime, date

import pandas

from app.store.reader import get_comment_files

d = date.today()
file_path = f'comments/{datetime(d.year, d.month, d.day).date()}.zip'


class TestComments(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        result = get_comment_files(file_path)
        z = zipfile.ZipFile(io.BytesIO(result), "r")
        z.extractall('temp_files')

    @classmethod
    def tearDownClass(cls):
        files = glob.glob('temp_files/*')
        for f in files:
            os.remove(f)

    def test_009_comments(self):
        result = pandas.read_excel('temp_files/009_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 009 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_017_comments(self):
        result = pandas.read_excel('temp_files/017_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 017 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_019_comments(self):
        result = pandas.read_excel('temp_files/019_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 019 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_023_comments(self):
        result = pandas.read_excel('temp_files/023_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 023 comment')
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

    def test_139_comments(self):
        result = pandas.read_excel('temp_files/139_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 139 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_144_comments(self):
        result = pandas.read_excel('temp_files/144_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 144 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_147_comments(self):
        result = pandas.read_excel('temp_files/147_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 147 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_160_comments(self):
        result = pandas.read_excel('temp_files/160_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 160 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_165_comments(self):
        result = pandas.read_excel('temp_files/165_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 165 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_182_comments(self):
        result = pandas.read_excel('temp_files/182_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 182 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_183_comments(self):
        result = pandas.read_excel('temp_files/183_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 183 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_184_comments(self):
        result = pandas.read_excel('temp_files/184_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 184 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_185_comments(self):
        result = pandas.read_excel('temp_files/185_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 185 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_187_comments(self):
        result = pandas.read_excel('temp_files/187_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 187 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_228_comments(self):
        result = pandas.read_excel('temp_files/228_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 228 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)

    def test_283_comments(self):
        result = pandas.read_excel('temp_files/283_201605.xls')

        self.assertEqual(result.iat[1, 3], 'I am a 283 comment')
        self.assertEqual(int(result.iat[1, 1]), 201605)
