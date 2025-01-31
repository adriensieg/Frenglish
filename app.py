from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import logging
import random

from services.firestore_service import add_entry, get_all_entries, update_entry, delete_entry, get_random_entry
from services.translation_service import TranslationService
from security.secretmanagerretriever import get_all_secrets
from config.config import config
from algorithms.data_processor import TranslationEntry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", template_folder="templates")

# Retrieve secrets
secrets = get_all_secrets()

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

firebase_admin.initialize_app(cred)
db = firestore.Client()

# Initialize translation service
translation_service = TranslationService(api_key=secrets['gemini_api_key'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/entries', methods=['GET'])
def get_entries():
    try:
        entries = get_all_entries(db)
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

        result = translation_service.process_translation(entry)
        doc_id = add_entry(db, result)

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

        update_entry(db, doc_id, entry)
        return jsonify({"message": "Entry updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/entries/<doc_id>', methods=['DELETE'])
def delete_entry_route(doc_id):
    try:
        if not doc_id:
            return jsonify({"error": "Invalid document ID"}), 400

        delete_entry(db, doc_id)
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
        processed_text = translation_service.process_consulting(input_text)

        return jsonify({
            "result": processed_text
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/random-entry', methods=['GET'])
def get_random_entry_route():
    try:
        entry_data = get_random_entry(db)
        return jsonify(entry_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
