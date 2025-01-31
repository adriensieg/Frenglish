import logging
from datetime import datetime
from typing import Dict, List
from firebase_admin import firestore
from algorithms.data_processor import TranslationEntry
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_entry(db: firestore.Client, entry: TranslationEntry) -> str:
    try:
        if not any([entry.english, entry.french]):
            raise ValueError("Entry must contain at least one non-empty field")

        # Add timestamp before storing
        entry.timestamp = datetime.now().timestamp()

        doc_ref = db.collection('Frenglish').document()
        doc_ref.set(entry.to_dict())
        return doc_ref.id
    except Exception as e:
        logger.error(f"Error adding entry: {e}")
        raise

def get_all_entries(db: firestore.Client) -> List[Dict[str, str]]:
    try:
        # Query entries ordered by timestamp in descending order
        docs = db.collection('Frenglish').order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
        entries = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            entries.append(data)
        return entries
    except Exception as e:
        logger.error(f"Error retrieving entries: {e}")
        raise

def update_entry(db: firestore.Client, doc_id: str, entry: TranslationEntry) -> None:
    try:
        if not doc_id:
            raise ValueError("Document ID is required for update")
        if not any([entry.english, entry.french]):
            raise ValueError("Entry must contain at least one non-empty field")

        # Preserve the original timestamp when updating
        original_doc = db.collection('Frenglish').document(doc_id).get()
        if original_doc.exists:
            original_data = original_doc.to_dict()
            entry.timestamp = original_data.get('timestamp', datetime.now().timestamp())
        else:
            entry.timestamp = datetime.now().timestamp()

        db.collection('Frenglish').document(doc_id).set(entry.to_dict())
    except Exception as e:
        logger.error(f"Error updating entry: {e}")
        raise

def delete_entry(db: firestore.Client, doc_id: str) -> None:
    try:
        if not doc_id:
            raise ValueError("Document ID is required for deletion")
        db.collection('Frenglish').document(doc_id).delete()
    except Exception as e:
        logger.error(f"Error deleting entry: {e}")
        raise

def get_random_entry(db: firestore.Client) -> Dict[str, str]:
    try:
        # Get all documents from the collection
        docs = list(db.collection('Frenglish').stream())

        if not docs:
            raise ValueError("No entries found")

        # Select a random document
        random_doc = random.choice(docs)

        # Convert the document to a dictionary and add the ID
        entry_data = random_doc.to_dict()
        entry_data['id'] = random_doc.id

        return entry_data
    except Exception as e:
        logger.error(f"Error retrieving random entry: {e}")
        raise
