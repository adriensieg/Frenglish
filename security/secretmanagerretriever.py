from google.cloud import secretmanager
import logging
from config.config import config

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def retrieve_secret(secret_id, project_id=config.SECRET_MANAGER_PROJECT_ID, version_id='latest'):
    """Retrieve a secret from Google Cloud Secret Manager."""
    logger.debug(f"Retrieving secret: {secret_id} from project: {project_id}, version: {version_id}")
    try:
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")
        logger.debug(f"Secret retrieved successfully: {secret_id}")
        return secret_value
    except Exception as e:
        logger.error(f"Error retrieving secret {secret_id}: {str(e)}")
        raise

def get_all_secrets():
    """Get all required secrets."""
    logger.debug(f"Getting all secrets for project: {config.SECRET_MANAGER_PROJECT_ID}")

    try:
        secrets = {
            'project_id': retrieve_secret('project_id'),
            'private_key_id_firestore_auth': retrieve_secret('private_key_id_firestore_auth'),
            'private_key_firestore_auth': retrieve_secret('private_key_firestore_auth').replace(r'\n', '\n'),
            'client_email_firestore_auth': retrieve_secret('client_email_firestore_auth'),
            'client_id_firestore_auth': retrieve_secret('client_id_firestore_auth'),
            'client_x509_cert': retrieve_secret('client_x509_cert'),
            'gemini_api_key': retrieve_secret('gemini_api_key')
        }
        logger.debug(f"Secrets retrieved successfully")
        return secrets
    except Exception as e:
        logger.error(f"Error retrieving all secrets: {str(e)}")
        raise
