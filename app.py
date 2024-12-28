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

# Firestore credentials
PROJECT_ID = "personal-sandbox-433116" 
PRIVATE_KEY_ID = "a7bdfd9a00b73c241efd2f7dfe39b131ce5ed236"
PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDCaxwYQbmRhATf
TmuQjCeW0/YK50/FOv5c/nGIEWcFfKd+yn2sv3e4llS+Y36x3MTU4TyAP23n71e0
y+kJC6hhcDMKYPG1J5fYTESJL39CeLiB7Deasvi2rupuTql0lUyBYHg6UfNq6n7Q
rO6sTmIz1vYxrnwBJVIRpsOQke+sp90aonRO4LvAjnS7s4GSvod1KplW45KDLmvs
PRX+vmxOpxVkUPz205oOS9wM1VnbRV+Z1gp8FSIS2BIumXUURqZA0vHenjrDNfEr
wOffAFwndCS/mDrU2w3A8YmqMRmkooGnoQKoSJbGvFzfpHQpG4w2z17ELOTz7JQk
+k1p+2cNAgMBAAECggEAHIRziYdSfeq8gDjThE9am0AaDf1h8Q83MlLMOmY7E032
j52KE6W+HOBIK+kSM2qroIItSq6DI4sy9T0XwJDqMOixQ+t2aNkW585AG1NROmHU
xpHskg+AdeNwVZ/KMWSY5T1ORVex+dPNqDRFihaxRuNYF299lvlvcVFhzDnrywpO
a1JLa/zinJxWSqitcvD1FAoCp0WE8x3rIlNtpH40SedUSWSKhCVoQ6xOHWJxqlKW
GUMvDWZ68X/UJUZTp8N9VUGBMbKafjZLjnkPRgrT2VLlMqWFVbbpO/VyZ5+BS3TY
AkKRG6thr9Le+Z8FccIXSGzDDoVLc7pKu5FdYMSlwQKBgQD8lNMUlY2hs1ubnA87
jBGFAJNki18lij11Oy4y1qyW7h8fDH37H8xcZT1g3dnSTCihKV91QUuGVdx/sM6t
KLnen7zTL20qeyDxSdqUmD9XGoJzQ+gp2kb1fLDdzvQq+u5V09CVjPZAmoM68Kto
QmLdRYDqWuQKe81rkG0halMvfQKBgQDFDMFEO85wUk5wpt9q0CbzWyEiYr91t4o+
IpHHEDZ01phBUMxg62cZoIUFCCPmczkslmeAamOM/ENZ5gnRQ9pnyt/IDLJ05ZuR
9RxP8eEqb5c3GeGL5kC3Omhk/ZE4Z3Fy+0rB5GxD7OF4T2AvYQxUOZt794JgUGVK
kI3kcE3K0QKBgBk8dWqVFrWVSg3eJdd5Qzbau99L3ZHOoh1YcGE7+bqKyCk+AkhZ
AP4qT1uiTuUoHtcbXyJEB9vAMGvBqqS6cPfBVghzsKCR9NSm4GQAYjO9vlLt8gBc
gsJ8Vt+SkerJb467vxdyIhiKV5pH+ZhNKbuZ+itwMWCqxfd9UqoICY+xAoGBAKQX
6xoXc+K1p/zH+mXI0ab2zLEF6srs/YKg5yUOq0rBKim6T3imkEUXF68JCFxwt7wZ
xDd8YUqXCL9kgehyyP6GQ7UkXbhbPSJfLCSnGQttwk9wjhMiu+HaEfWH89c0zZUj
Dy5IOqCWM20tLLxH5Sx+jKy/gSMT0EY3+vGxVBcBAoGAbEzH6aYxFNge9kUyBXHs
yYEnunxju99EONIhN7llqskyiXttxCLSifM0OQurgoZj7WvwBK88HxpQjDls+dfK
1cZqQkAHryiQDvm8ghWZwURVMgc8fA5SxTBcH4ZlDhgYxK2TjjFn/lMi6UhwpORT
tzZoGuUSHSvgroBQOdqSINE=
-----END PRIVATE KEY-----
"""
CLIENT_ID = "107679320816609162297"
CLIENT_EMAIL = "firestore-backend-sa@personal-sandbox-433116.iam.gserviceaccount.com"
CLIENT_X509_CERT = "https://www.googleapis.com/robot/v1/metadata/x509/firestore-backend-sa%40personal-sandbox-433116.iam.gserviceaccount.com"

# Initialize Firebase Admin SDK
cred = credentials.Certificate({
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
})

firebase_admin.initialize_app(cred)
db = firestore.Client()
collection = db.collection('Frenglish')

def add_entry(entry: TranslationEntry) -> str:
    try:
        if not any([entry.english, entry.french]):
            raise ValueError("Entry must contain at least one non-empty field")
        doc_ref = collection.document()
        doc_ref.set(entry.to_dict())
        return doc_ref.id
    except Exception as e:
        logger.error(f"Error adding entry: {e}")
        raise

def get_all_entries() -> List[Dict[str, str]]:
    try:
        docs = collection.stream()
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
        collection.document(doc_id).set(entry.to_dict())
    except Exception as e:
        logger.error(f"Error updating entry: {e}")
        raise

def delete_entry(doc_id: str) -> None:
    try:
        if not doc_id:
            raise ValueError("Document ID is required for deletion")
        collection.document(doc_id).delete()
    except Exception as e:
        logger.error(f"Error deleting entry: {e}")
        raise

CONFIG = {
    "api_key": "AIzaSyBhCB1cO0ZUzRB0DYBCz4zcMwS9kVy_ruU",
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

if __name__ == '__main__':
    app.run(debug=True)
