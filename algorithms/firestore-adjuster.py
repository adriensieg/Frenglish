from datetime import datetime, timedelta
import time
import firebase_admin
from firebase_admin import credentials, firestore

# Firestore credentials
PROJECT_ID = "" 
PRIVATE_KEY_ID = ""
PRIVATE_KEY = ""
CLIENT_ID = ""
CLIENT_EMAIL = ""
CLIENT_X509_CERT = ""

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


if __name__ == "__main__":
    try:
        collection_ref = db.collection('Frenglish')
    
        # Get all documents in the collection
        docs = collection_ref.stream()
        
        for doc in docs:
            doc_data = doc.to_dict()
            doc_ref = collection_ref.document(doc.id)
            
            # Check if timestamp field exists
            if 'timestamp' not in doc_data:
                # Calculate timestamp from two days ago
                two_days_ago = datetime.now() - timedelta(days=2)
                timestamp = two_days_ago.timestamp()
                
                # Update document with new timestamp
                doc_ref.update({
                    'timestamp': timestamp
                })
                print(f"Added timestamp to document {doc.id}")
            else:
                print(f"Document {doc.id} already has timestamp field")

        print("Processing completed successfully")
    except Exception as e:
        print(f"An error occurred: {str(e)}")