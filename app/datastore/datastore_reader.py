
from app.datastore import DATASTORE_CLIENT, QUARANTINE_KIND
import structlog

logger = structlog.get_logger()


def fetch_quarantined_messages() -> list:
	"""
	Returns a list of the entities in the GCP for the "quarantine_messages" kind
	Returns list of google entity objects
	"""
	kind = QUARANTINE_KIND
	quarantine_messages = []
	try:
		query = DATASTORE_CLIENT.query(kind=kind)
		for entity in query.fetch():
			tx_id = entity["key"]["id_or_name"]
			quarantine_messages.append(tx_id)
	except Exception as e:
		logger.error(f'Datastore error fetching entities: {e}')

	finally:
		return quarantine_messages

