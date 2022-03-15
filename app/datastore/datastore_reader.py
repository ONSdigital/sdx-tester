from datetime import date, datetime, timedelta

from app.datastore import DATASTORE_CLIENT, QUARANTINE_KIND, DATASTORE_TOOLBOX_CLIENT
import structlog


logger = structlog.get_logger()


def fetch_quarantined_messages() -> list:
    """
    Returns list of tx_id's quarantined in DataStore
    """
    kind = QUARANTINE_KIND
    quarantine_messages = []
    try:
        query = DATASTORE_TOOLBOX_CLIENT.query(kind=kind)
        for entity in query.fetch():
            tx_id = entity.key.id_or_name
            quarantine_messages.append(tx_id)
    except Exception as e:
        logger.error(f'Datastore error fetching entities: {e}')

    finally:
        return quarantine_messages


def get_entity_count(kind: str) -> int:
    """
    Returns the number of rows that matches the filter
    """
    logger.info('Checking if comments')
    d = date.today()
    ninety_days_ago = datetime(d.year, d.month, d.day) - timedelta(days=90)
    query = DATASTORE_CLIENT.query(kind=kind)
    query.add_filter("created", "<", ninety_days_ago)
    return len(list(query.fetch()))


def fetch_comment_kinds() -> list:
    """
        Fetch a list of all comment kinds from datastore.
        Each kind is represented by {survey_id}_{period}
    """
    try:
        query = DATASTORE_CLIENT.query(kind="__kind__")
        query.keys_only()
        return [entity.key.id_or_name for entity in query.fetch() if not entity.key.id_or_name.startswith("_")]
    except Exception as e:
        print(f'Datastore error fetching kinds: {e}')
        raise e
