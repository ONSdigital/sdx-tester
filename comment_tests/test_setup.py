import os
import pprint
import unittest
import uuid
from datetime import date, datetime, timedelta
from google.cloud import datastore, exceptions
from app import CONFIG, cloud_config
from comment_tests.comment_encrypt import encrypt_comment

COMMENT_KEY = "E3rjFT2i9ALcvc99Pe3YqjIGrzm3LdMsCXc8nUaOEbc="


class TestSetup(unittest.TestCase):

    unittest.TestLoader.sortTestMethodsUsing = None
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
        cloud_config()

    def test_datastore_cleanup(self):
        try:
            query = CONFIG.DATASTORE_CLIENT.query(kind='Comment')
            results = list(query.fetch())
            CONFIG.DATASTORE_CLIENT.delete_multi(results)
            print('successfully deleted all comments:')
            pprint.pprint(results)

        except Exception as e:
            print(e)
            print('Failed to delete item from Datastore')
        return True

    def test_bucket_cleanup(self):
        try:
            bucket = CONFIG.BUCKET
            blob = bucket.blob('comments')
            blob.delete()
            print("Blob {} deleted.".format('comments folder'))
        except exceptions.NotFound as error:
            print(error)

    def test_insert_comments(self):
        d = date.today()
        today = datetime(d.year, d.month, d.day)
        yesterday = today - timedelta(1)

        for survey_id in self.surveys:
            create_entity(survey_id, yesterday)

        survey_134 = datastore.Entity(CONFIG.DATASTORE_CLIENT.key("Comment", str(uuid.uuid4())))

        survey_134.update(
            {
                "created": str(yesterday),
                "encrypted_data": encrypt_comment({"ru_ref": "12346789012A",
                                                   "boxes_selected": "91w, 95w, 96w, 97w, 91f, 95f, 96f, 97f, 191m, 195m, 196m, 197m, 191w4, 195w4, 196w4, 197w4, 191w5, 195w5, 196w5, 197w5, ",
                                                   "comment": "flux clean",
                                                   "additional": [{"qcode": "300w", "comment": "Pipe mania"},
                                                                  {"qcode": "300f", "comment": "Gas leak"},
                                                                  {"qcode": "300m", "comment": "copper pipe"},
                                                                  {"qcode": "300w4", "comment": "solder joint"},
                                                                  {"qcode": "300w5", "comment": "drill hole"}]}),
                "period": 201605,
                "survey_id": "134",
            }
        )
        CONFIG.DATASTORE_CLIENT.put(survey_134)

        print(f'Successfully put 134 into Datastore')


def create_entity(survey_id, date_stored):
    survey_entity = datastore.Entity(CONFIG.DATASTORE_CLIENT.key("Comment", str(uuid.uuid4())))

    survey_entity.update(
        {
            "created": str(date_stored),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '12346789012A', 'boxes_selected': '', 'comment': f'I am a {survey_id} comment',
                 'additional': []}
            ),
            "period": 201605,
            "survey_id": survey_id,
        }
    )
    CONFIG.DATASTORE_CLIENT.put(survey_entity)
    print(f'Successfully put {survey_id} into Datastore')
