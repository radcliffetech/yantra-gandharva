import os
from datetime import datetime

import firebase_admin
from colorama import Fore, Style
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
    try:
        print(
            Fore.YELLOW
            + f"📤 Uploading file to Firebase Storage: {local_path} → outputs/{remote_filename}"
        )
        blob = bucket.blob(f"outputs/{remote_filename}")
        blob.upload_from_filename(local_path)
        blob.make_public()
        print(Fore.GREEN + f"✅ Upload successful: {blob.public_url}" + Style.RESET_ALL)
        return blob.public_url
    except Exception as e:
        print(Fore.RED + f"❌ Upload failed: {e}" + Style.RESET_ALL)
        raise


# Save realization metadata to Firestore
def save_realization_metadata(realization_data: dict) -> str:
    try:
        print(Fore.YELLOW + "📝 Saving realization metadata to Firestore...")
        doc_ref = db.collection(COLLECTION_ID).document()
        realization_data["created_at"] = datetime.utcnow().isoformat()
        doc_ref.set(realization_data)
        print(
            Fore.GREEN
            + f"✅ Metadata saved. Document ID: {doc_ref.id}"
            + Style.RESET_ALL
        )
        return doc_ref.id
    except Exception as e:
        print(Fore.RED + f"❌ Firestore write failed: {e}" + Style.RESET_ALL)
        raise


# Fetch all realizations from Firestore
def fetch_all_realizations() -> list[dict]:
    try:
        print(Fore.YELLOW + "📥 Fetching all realizations from Firestore...")
        docs = db.collection(COLLECTION_ID).stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            results.append(data)
        print(
            Fore.GREEN + f"✅ Retrieved {len(results)} realizations." + Style.RESET_ALL
        )
        return results
    except Exception as e:
        print(Fore.RED + f"❌ Failed to fetch realizations: {e}" + Style.RESET_ALL)
        raise
