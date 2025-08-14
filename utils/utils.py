from pathlib import Path
from google.cloud import storage
from google.oauth2 import service_account
from utils.constants import logger


def initialize_gcs_client(service_account_path: Path) -> storage.Client:
    """
    Initialize a Google Cloud Storage client.

    Parameters
    ----------
    service_account_path : Union[str, Path]
        Path to the service account JSON file.

    Returns
    -------
    storage.Client
        GCS client instance.
    """
    try:
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path
        )
        client = storage.Client(credentials=credentials, project=credentials.project_id)
        logger.info("GSC Credentials Initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Couldn't create a GCS client: {e}")
        raise
