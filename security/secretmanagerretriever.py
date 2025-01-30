from google.cloud import secretmanager
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def retrieve_secret(secret_id, project_id, version_id='latest'):
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

def get_all_secrets(PROJECT_ID):
    """Get all required secrets."""
    logger.debug(f"Getting all secrets for project: {PROJECT_ID}")
    
    try:
        secrets = {
            'project_id': retrieve_secret('project_id', PROJECT_ID),
            'private_key_id_firestore_auth': retrieve_secret('private_key_id_firestore_auth', PROJECT_ID),
            'private_key_firestore_auth': retrieve_secret('private_key_firestore_auth', PROJECT_ID).replace(r'\n', '\n'),
            'client_email_firestore_auth': retrieve_secret('client_email_firestore_auth', PROJECT_ID),
            'client_id_firestore_auth': retrieve_secret('client_id_firestore_auth', PROJECT_ID),
            'client_x509_cert_url': retrieve_secret('client_x509_cert_url', PROJECT_ID),
            'gemini_api_key': retrieve_secret('gemini_api_key', PROJECT_ID)
        }
        logger.debug(f"Secrets retrieved with success")
        return secrets
    except Exception as e:
        logger.error(f"Error retrieving all secrets: {str(e)}")
        raise
