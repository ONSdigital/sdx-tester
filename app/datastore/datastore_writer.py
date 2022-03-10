from google.cloud import datastore
from app.datastore import DATASTORE_CLIENT
import structlog

from app.datastore.datastore_reader import fetch_comment_kinds

logger = structlog.get_logger()


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

