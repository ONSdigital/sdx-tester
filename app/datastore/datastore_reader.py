from app.datastore import DATASTORE_CLIENT, QUARANTINE_KIND
import structlog

logger = structlog.get_logger()


def fetch_quarantined_messages() -> list:
	"""
	Returns list of tx_id's quarantined in DataStore
	"""
	kind = QUARANTINE_KIND
	quarantine_messages = []
	try:
		query = DATASTORE_CLIENT.query(kind=kind)
		for entity in query.fetch():
			tx_id = entity.key.id_or_name
			quarantine_messages.append(tx_id)
	except Exception as e:
		logger.error(f'Datastore error fetching entities: {e}')

	finally:
		return quarantine_messages

