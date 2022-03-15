import json

import structlog
from cryptography.fernet import Fernet
from google.cloud import datastore

from app.datastore import PROJECT_ID, DATASTORE_CLIENT
from app.datastore.datastore_reader import fetch_comment_kinds
from app.secret_manager import get_secret

logger = structlog.get_logger()


COMMENT_KEY = get_secret(PROJECT_ID, 'sdx-comment-key')


def write_entity(kind: str, entity_id: str, data: dict, exclude_from_indexes: tuple = ()):
    key = DATASTORE_CLIENT.key(kind, entity_id)
    entity = datastore.Entity(key, exclude_from_indexes=exclude_from_indexes)
    entity.update(data)
    DATASTORE_CLIENT.put(entity)
    print(f'Successfully wrote {entity_id} to {kind} in Datastore')


def cleanup_datastore():
    try:
        kinds = fetch_comment_kinds()
        for kind in kinds:
            query = DATASTORE_CLIENT.query(kind=kind)
            query.keys_only()
            keys = [entity.key for entity in query.fetch()]
            logger.info("Cleaning datastore")
            DATASTORE_CLIENT.delete_multi(keys)
            if not fetch_comment_kinds():
                logger.info(f'successfully deleted {keys} from Datastore')

    except Exception as e:
        print(e)
        logger.error('Failed to delete item from Datastore')
    return True


def encrypt_comment(data: dict) -> str:
    comment_str = json.dumps(data)
    f = Fernet(COMMENT_KEY)
    token = f.encrypt(comment_str.encode())
    return token.decode()
