from typing import Dict, List
from dataclasses import dataclass
import logging

from flask import Flask, render_template, request, jsonify, send_from_directory

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

from algorithms.data_processor import GeminiProcessor
from algorithms.prompts import translation, sentences, bcg_consultant

import os
import random

from security.secretmanagerretriever import get_all_secrets

PROJECT_ID = '183061022621'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", template_folder="templates")

@dataclass
class TranslationEntry:
    english: str
    french: str
    context: str
    notes: str = ""
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, str]:
        return {
            "english": self.english if self.english else "",
            "french": self.french if self.french else "",
            "context": self.context if self.context else "",
            "notes": self.notes if self.notes else "",
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(data: Dict[str, str]) -> 'TranslationEntry':
        return TranslationEntry(
            english=data.get("english", ""),
            french=data.get("french", ""),
            context=data.get("context", ""),
            notes=data.get("notes", ""),
            timestamp=data.get("timestamp", 0.0)
        )

secrets = get_all_secrets(PROJECT_ID)

# Initialize Firebase Admin SDK
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": secrets['project_id'],
    "private_key_id": secrets['private_key_id_firestore_auth'],
    "private_key": secrets['private_key_firestore_auth'],
    "client_email": secrets['client_email_firestore_auth'],
    "client_id": secrets['client_id_firestore_auth'],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": secrets['client_x509_cert'],
    "universe_domain": "googleapis.com"
})

CONFIG = {
    "api_key": secrets['gemini_api_key'],
    "model_name": "gemini-2.0-flash-exp"
}

firebase_admin.initialize_app(cred)
db = firestore.Client()

def add_entry(entry: TranslationEntry) -> str:
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

def get_all_entries() -> List[Dict[str, str]]:
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

def update_entry(doc_id: str, entry: TranslationEntry) -> None:
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

def delete_entry(doc_id: str) -> None:
    try:
        if not doc_id:
            raise ValueError("Document ID is required for deletion")
        db.collection('Frenglish').document(doc_id).delete()
    except Exception as e:
        logger.error(f"Error deleting entry: {e}")
        raise

processor = GeminiProcessor(
    api_key=CONFIG["api_key"],
    model_name=CONFIG["model_name"]
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/entries', methods=['GET'])
def get_entries():
    try:
        entries = get_all_entries()
        return jsonify(entries)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/entries', methods=['POST'])
def add_entry_route():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        entry = TranslationEntry(
            english=data.get('english', ''),
            french=data.get('french', ''),
            context=data.get('context', ''),
            notes=data.get('notes', '')
        )

        if entry.french:
            result = TranslationEntry(
                english=processor.traduction_vocabulary(translation, entry.french),
                french=entry.french,
                context=processor.traduction_vocabulary(sentences, entry.french),
                notes=""
            )
        elif entry.english:
            result = TranslationEntry(
                english=entry.english,
                french=processor.traduction_vocabulary(translation, entry.english),
                context=processor.traduction_vocabulary(sentences, entry.english),
                notes=""
            )
        else:
            return jsonify({"error": "Entry must contain English or French"}), 400

        doc_id = add_entry(result)
        
        # Return the complete result data
        return jsonify({
            "id": doc_id,
            "message": "Entry added successfully",
            "english": result.english,
            "french": result.french,
            "context": result.context,
            "notes": result.notes,
            "timestamp": result.timestamp
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/entries/<doc_id>', methods=['PUT'])
def update_entry_route(doc_id):
    try:
        if not doc_id:
            return jsonify({"error": "Invalid document ID"}), 400

        data = request.json
        entry = TranslationEntry(
            english=data.get('english', ''),
            french=data.get('french', ''),
            context=data.get('context', ''),
            notes=data.get('notes', '')
        )

        update_entry(doc_id, entry)
        return jsonify({"message": "Entry updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/entries/<doc_id>', methods=['DELETE'])
def delete_entry_route(doc_id):
    try:
        if not doc_id:
            return jsonify({"error": "Invalid document ID"}), 400

        delete_entry(doc_id)
        return jsonify({"message": "Entry deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/consulting', methods=['POST'])
def process_consulting():
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400
            
        input_text = data.get('text', '')
        processed_text = processor.traduction_vocabulary(bcg_consultant, input_text),
        
        return jsonify({
            "result": processed_text
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/random-entry', methods=['GET'])
def get_random_entry():
    try:
        # Get all documents from the collection
        docs = list(db.collection('Frenglish').stream())
        
        if not docs:
            return jsonify({"error": "No entries found"}), 404
            
        # Select a random document
        random_doc = random.choice(docs)
        
        # Convert the document to a dictionary and add the ID
        entry_data = random_doc.to_dict()
        entry_data['id'] = random_doc.id
        
        return jsonify(entry_data)
    except Exception as e:
        logger.error(f"Error retrieving random entry: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)