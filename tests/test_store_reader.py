import unittest

from app import store_reader


class TestReader(unittest.TestCase):

    def test_get_filename(self):
        data = '{"version": "1", "files": [{"name": "c37a3efa-593c-4bab-b49c-bee0613c4fb4.json", ' \
               '"URL": "http://sdx-store:5000/responses/c37a3efa-593c-4bab-b49c-bee0613c4fb4", "sizeBytes": "2135", ' \
               '"md5sum": "09da1a5f13ae89789d75a96db61a91d4"}], "sensitivity": "High", "sourceName": ' \
               '"sdx_development", "manifestCreated": "2020-12-10T11:09:29.148Z", "description": "283 survey response ' \
               'for period 201605 sample unit 11842491738S", "iterationL1": "201605", "dataset": "283", ' \
               '"schemaversion": "1"} '
        expected = "c37a3efa-593c-4bab-b49c-bee0613c4fb4"
        actual = store_reader.get_filename(data)
        self.assertEqual(expected, actual)
