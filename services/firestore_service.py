import logging
from datetime import datetime
from typing import Dict, List, Optional
from firebase_admin import firestore
from algorithms.data_processor import TranslationEntry
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COLLECTION_NAME = "Frenglish"

def add_entry(db: firestore.Client, entry: TranslationEntry) -> str:
    """Adds a translation entry to Firestore."""
    if not any([entry.english, entry.french]):
        raise ValueError("Entry must contain at least one non-empty field")
    
    entry.timestamp = datetime.utcnow().timestamp()
    doc_ref = db.collection(COLLECTION_NAME).document()
    doc_ref.set(entry.to_dict())
    logger.info(f"Entry added with ID: {doc_ref.id}")
    return doc_ref.id

def get_all_entries(db: firestore.Client) -> List[Dict[str, str]]:
    """Retrieves all translation entries from Firestore, ordered by timestamp descending."""
    try:
        docs = db.collection(COLLECTION_NAME).order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
        entries = [{**doc.to_dict(), "id": doc.id} for doc in docs]
        logger.info(f"Retrieved {len(entries)} entries.")
        return entries
    except Exception as e:
        logger.exception("Error retrieving entries")
        raise

def update_entry(db: firestore.Client, doc_id: str, entry: TranslationEntry) -> None:
    """Updates an existing translation entry in Firestore while preserving the original timestamp."""
    if not doc_id:
        raise ValueError("Document ID is required for update")
    if not any([entry.english, entry.french]):
        raise ValueError("Entry must contain at least one non-empty field")
    
    doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
    original_doc = doc_ref.get()
    
    if not original_doc.exists:
        raise ValueError("Document not found")
    
    original_data = original_doc.to_dict()
    entry.timestamp = original_data.get("timestamp", datetime.utcnow().timestamp())
    doc_ref.set(entry.to_dict())
    logger.info(f"Entry {doc_id} updated.")

def delete_entry(db: firestore.Client, doc_id: str) -> None:
    """Deletes a translation entry from Firestore."""
    if not doc_id:
        raise ValueError("Document ID is required for deletion")
    
    db.collection(COLLECTION_NAME).document(doc_id).delete()
    logger.info(f"Entry {doc_id} deleted.")

def get_random_entry(db: firestore.Client) -> Optional[Dict[str, str]]:
    """Retrieves a random translation entry from Firestore."""
    try:
        docs = list(db.collection(COLLECTION_NAME).stream())
        if not docs:
            logger.warning("No entries found.")
            return None
        random_doc = random.choice(docs)
        entry_data = {**random_doc.to_dict(), "id": random_doc.id}
        logger.info(f"Random entry retrieved: {entry_data['id']}")
        return entry_data
    except Exception as e:
        logger.exception("Error retrieving random entry")
        raise
