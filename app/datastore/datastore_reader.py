
from app.datastore import DATASTORE_CLIENT, QUARANTINE_KIND
logger = structlog.get_logger()

def fetch_quarantined_messages() -> list:
	"""
	Returns a list of the entities in the GCP for the "quarantine_messages" kind
	"""
	kind = QUARANTINE_KIND
	try:
		query = DATASTORE_CLIENT.query(kind=kind)
		return list(query.fetch())
	except Exception as e:
		logger.error(f'Datastore error fetching entities: {e}')

