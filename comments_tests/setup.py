from datetime import date, datetime, timedelta
from google.cloud import datastore, storage
from app import PROJECT_ID
from comments_tests.comment_encrypt import encrypt_comment

datastore_client = datastore.Client(project=PROJECT_ID)


def run_comments():
    # Delete everything from Datastore
    datastore_cleanup()
    # Delete comments folder in the bucket
    bucket_cleanup()
    # Fill Datastore with comments
    insert_comments()
    # Trigger cronjob
    # Look in bucket, decrypt and validate
    pass


def datastore_cleanup():
    try:
        query = datastore_client.query(kind='Comment')
        results = list(query.fetch())
        datastore_client.delete_multi(results)
        print(f'successfully deleted all comments: {results}')

    except Exception as e:
        print(e)
        print('Failed to delete item from Datastore')


def bucket_cleanup():
    bucket_name = 'ons-sdx-tom-outputs'
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob('comments')
    blob.delete()
    print("Blob {} deleted.".format('comments folder'))


def insert_comments():
    d = date.today()
    today = datetime(d.year, d.month, d.day).date()
    yesterday = today - timedelta(1)

    survey_009 = datastore.Entity(datastore_client.key("Comment", '9db49fb8-4bcc-4615-b42c-b2ab80b234b8'))

    survey_009.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '34650525171T', 'boxes_selected': '', 'comment': 'I am a 009 comment', 'additional': []}
            ),
            "period": 201605,
            "survey_id": "009",
        }
    )

    survey_017 = datastore.Entity(datastore_client.key("Comment", 'bd1868be-def1-4e17-b695-a1ac5fbb76af'))

    survey_017.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '34650525171T', 'boxes_selected': '', 'comment': 'I am a 017 comment', 'additional': []}),
            "period": 201605,
            "survey_id": "017",
        }
    )

    survey_019 = datastore.Entity(datastore_client.key("Comment", 'ea31f745-5c5e-47b6-8086-09af0d9d6377'))

    survey_019.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '34650525171T', 'boxes_selected': '', 'comment': 'I am a 019 comment', 'additional': []}),
            "period": 201605,
            "survey_id": "019",
        }
    )

    survey_023 = datastore.Entity(datastore_client.key("Comment", '063a379d-1472-4395-9a4e-d6ee13362b16'))

    survey_023.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '34650525171T', 'boxes_selected': '', 'comment': 'I am a 023 comment', 'additional': []}),
            "period": 201605,
            "survey_id": "023",
        }
    )

    survey_134 = datastore.Entity(datastore_client.key("Comment", 'a5259d77-67e4-403b-a1a0-ac16301b68bf'))

    survey_134.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment({"ru_ref": "12346789012A", "boxes_selected": "91w, 95w, 96w, 97w, 91f, 95f, 96f, 97f, ' \
             '191m, 195m, 196m, 197m, 191w4, 195w4, 196w4, 197w4, 191w5, 195w5, 196w5, 197w5, ", "comment": "flux ' \
             'clean", "additional": [{"qcode": "300w", "comment": "Pipe mania"}, {"qcode": "300f", "comment": "Gas ' \
             'leak"}, {"qcode": "300m", "comment": "copper pipe"}, {"qcode": "300w4", "comment": "solder joint"},
                                     {"qcode": "300w5", "comment": "drill hole"}]}),
            "period": 201605,
            "survey_id": "134",
        }
    )

    survey_139 = datastore.Entity(datastore_client.key("Comment", '42e66ebd-bbc2-4593-a66a-7b07db3d5da2'))

    survey_139.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '34650525171T', 'boxes_selected': '', 'comment': 'I am a 139 comment', 'additional': []}
            ),
            "period": 201605,
            "survey_id": "139",
        }
    )

    survey_144 = datastore.Entity(datastore_client.key("Comment", '2ef6cd0b-0dd9-4c8d-a19c-f4ef6056ecd9'))

    survey_144.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '34650525171T', 'boxes_selected': '', 'comment': 'I am a 144 comment', 'additional': []}
            ),
            "period": 201605,
            "survey_id": "144",
        }
    )

    survey_147 = datastore.Entity(datastore_client.key("Comment", 'f87c2d41-25cb-406b-9400-11c85328763d'))

    survey_147.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '34650525171T', 'boxes_selected': '', 'comment': 'I am a 147 comment', 'additional': []}
            ),
            "period": 201605,
            "survey_id": "147",
        }
    )

    survey_160 = datastore.Entity(datastore_client.key("Comment", '07a05dee-20e5-4a65-93ed-f20848ac92de'))

    survey_160.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '34650525171T', 'boxes_selected': '', 'comment': 'I am a 160 comment', 'additional': []}
            ),
            "period": 201605,
            "survey_id": "160",
        }
    )

    survey_165 = datastore.Entity(datastore_client.key("Comment", '115b9cff-25ad-45cd-b141-38c9a31df3ac'))

    survey_165.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '34650525171T', 'boxes_selected': '', 'comment': 'I am a 165 comment', 'additional': []}
            ),
            "period": 201605,
            "survey_id": "165",
        }
    )

    survey_169 = datastore.Entity(datastore_client.key("Comment", '57b3eb1c-65a2-4f51-8c31-95e275e786aa'))

    survey_169.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '34650525171T', 'boxes_selected': '', 'comment': 'I am a 169 comment', 'additional': []}
            ),
            "period": 201605,
            "survey_id": "169",
        }
    )

    survey_182 = datastore.Entity(datastore_client.key("Comment", '7e7716bf-ee26-4ec1-bfc7-0d5cdb3ef12a'))

    survey_182.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '34650525171T', 'boxes_selected': '', 'comment': 'I am a 182 comment', 'additional': []}
            ),
            "period": 201605,
            "survey_id": "182",
        }
    )

    survey_183 = datastore.Entity(datastore_client.key("Comment", '4e5793a8-4f16-4e54-9e20-94c704794e0a'))

    survey_183.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '34650525171T', 'boxes_selected': '', 'comment': 'I am a 183 comment', 'additional': []}
            ),
            "period": 201605,
            "survey_id": "183",
        }
    )

    survey_184 = datastore.Entity(datastore_client.key("Comment", '0cc4c465-142d-47da-8232-89ddc399e633'))

    survey_184.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '34650525171T', 'boxes_selected': '', 'comment': 'I am a 184 comment', 'additional': []}
            ),
            "period": 201605,
            "survey_id": "184",
        }
    )

    survey_185 = datastore.Entity(datastore_client.key("Comment", '675ee2cc-bf16-49ed-90c6-edcf7c4c0b4c'))

    survey_185.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '34650525171T', 'boxes_selected': '', 'comment': 'I am a 185 comment', 'additional': []}
            ),
            "period": 201605,
            "survey_id": "185",
        }
    )

    survey_187 = datastore.Entity(datastore_client.key("Comment", 'ab175431-3cd6-4943-8a57-8d72524b79fe'))

    survey_187.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '12346789012A', 'boxes_selected': '', 'comment': 'I am a 187 comment', 'additional': []}
            ),
            "period": 201605,
            "survey_id": "187",
        }
    )

    survey_228 = datastore.Entity(datastore_client.key("Comment", 'db8e8768-842a-400b-bf37-16c973b1a926'))

    survey_228.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '12346789012A', 'boxes_selected': '', 'comment': 'I am a 228 comment', 'additional': []}
            ),
            "period": 201605,
            "survey_id": "228",
        }
    )

    survey_283 = datastore.Entity(datastore_client.key("Comment", '83b03406-b948-414a-8a54-4de730287a70'))

    survey_283.update(
        {
            "created": str(yesterday),
            "encrypted_data": encrypt_comment(
                {'ru_ref': '12346789012A', 'boxes_selected': '', 'comment': 'I am a 283 comment', 'additional': []}
            ),
            "period": 201605,
            "survey_id": "282",
        }
    )

    datastore_client.put_multi([survey_009,
                                survey_017,
                                survey_019,
                                survey_023,
                                survey_134,
                                survey_139,
                                survey_144,
                                survey_147,
                                survey_160,
                                survey_165,
                                survey_182,
                                survey_183,
                                survey_184,
                                survey_185,
                                survey_187,
                                survey_228,
                                survey_283])
