import os
from datetime import datetime

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore, storage

load_dotenv()

COLLECTION_ID = "realizations_v1"
STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")

if not STORAGE_BUCKET:
    raise ValueError("FIREBASE_STORAGE_BUCKET environment variable is not set.")

_service_key_path = os.path.join(
    os.path.dirname(__file__), "../../serviceAccountKey.json"
)


if not firebase_admin._apps:
    cred = credentials.Certificate(_service_key_path)
    firebase_admin.initialize_app(cred, {"storageBucket": STORAGE_BUCKET})

db = firestore.client()
bucket = storage.bucket()


# Upload a file to Cloud Storage and return its public URL
def upload_file_to_storage(local_path: str, remote_filename: str) -> str:
    blob = bucket.blob(f"outputs/{remote_filename}")
    blob.upload_from_filename(local_path)
    blob.make_public()  # Optional: make file publicly accessible
    return blob.public_url


# Save realization metadata to Firestore
def save_realization_metadata(realization_data: dict) -> str:
    doc_ref = db.collection(COLLECTION_ID).document()
    realization_data["created_at"] = datetime.utcnow().isoformat()
    doc_ref.set(realization_data)
    return doc_ref.id
