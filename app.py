from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from algorithms.data_processor import GeminiProcessor
from algorithms.prompts import translation, sentences

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@dataclass
class TranslationEntry:
    english: str
    french: str
    context: str
    notes: str = ""
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "english": self.english if self.english else "",
            "french": self.french if self.french else "",
            "context": self.context if self.context else "",
            "notes": self.notes if self.notes else ""
        }
    
    @staticmethod
    def from_dict(data: Dict[str, str]) -> 'TranslationEntry':
        return TranslationEntry(
            english=data.get("english", ""),
            french=data.get("french", ""),
            context=data.get("context", ""),
            notes=data.get("notes", "")
        )

class FrenglishDatabase:
    def __init__(self):
        PROJECT_ID = "personal-sandbox-433116"
        PRIVATE_KEY_ID = ""
        PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
-----END PRIVATE KEY-----
"""
        CLIENT_ID = "107679320816609162297"
        CLIENT_EMAIL = "firestore-backend-sa@personal-sandbox-433116.iam.gserviceaccount.com"
        CLIENT_X509_CERT = "https://www.googleapis.com/robot/v1/metadata/x509/firestore-backend-sa%40personal-sandbox-433116.iam.gserviceaccount.com"

        cred_dict = {
            "type": "service_account",
            "project_id": PROJECT_ID,
            "private_key_id": PRIVATE_KEY_ID,
            "private_key": PRIVATE_KEY,
            "client_email": CLIENT_EMAIL,
            "client_id": CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": CLIENT_X509_CERT,
            "universe_domain": "googleapis.com"
        }

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
        self.collection = self.db.collection('Frenglish')

    def add_entry(self, entry: TranslationEntry) -> str:
        try:
            if not any([entry.english, entry.french]):
                raise ValueError("Entry must contain at least one non-empty field")
            doc_ref = self.collection.document()
            doc_ref.set(entry.to_dict())
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error adding entry: {e}")
            raise

    def get_all_entries(self) -> List[Dict[str, str]]:
        try:
            docs = self.collection.stream()
            entries = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                entries.append(data)
            return entries
        except Exception as e:
            logger.error(f"Error retrieving entries: {e}")
            raise

    def update_entry(self, doc_id: str, entry: TranslationEntry) -> None:
        try:
            if not doc_id:
                raise ValueError("Document ID is required for update")
            if not any([entry.english, entry.french]):
                raise ValueError("Entry must contain at least one non-empty field")
            self.collection.document(doc_id).set(entry.to_dict())
        except Exception as e:
            logger.error(f"Error updating entry: {e}")
            raise

    def delete_entry(self, doc_id: str) -> None:
        try:
            if not doc_id:
                raise ValueError("Document ID is required for deletion")
            self.collection.document(doc_id).delete()
        except Exception as e:
            logger.error(f"Error deleting entry: {e}")
            raise

db = FrenglishDatabase()


CONFIG = {
    "api_key": "",
    "model_name": "gemini-2.0-flash-exp"
}

# Initialize processor
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
        entries = db.get_all_entries()
        return jsonify(entries)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/entries', methods=['POST'])
def add_entry():
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
                english = processor.traduction_vocabulary(translation, entry.french),
                french = entry.french,
                context = processor.traduction_vocabulary(sentences, entry.french),
                notes = ""
            )
        elif entry.english:
            result = TranslationEntry(
                english =  entry.english,
                french = processor.traduction_vocabulary(translation, entry.english),
                context = processor.traduction_vocabulary(sentences, entry.english),
                notes = ""
            )
        else:
            print('Nothing has been done')

        print(result)

        doc_id = db.add_entry(result)
        return jsonify({"id": doc_id, "message": "Entry added successfully"}), 201
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
        
        db.update_entry(doc_id, entry)
        return jsonify({"message": "Entry updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/entries/<doc_id>', methods=['DELETE'])
def delete_entry_route(doc_id):
    try:
        if not doc_id:
            return jsonify({"error": "Invalid document ID"}), 400
        
        db.delete_entry(doc_id)
        return jsonify({"message": "Entry deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
