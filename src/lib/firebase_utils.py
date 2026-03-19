import logging
import os
from datetime import datetime, timezone

from colorama import Fore
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

COLLECTION_ID = "realizations_v1"
STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")

_firebase_available = False
db = None
bucket = None

if STORAGE_BUCKET:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore, storage

        _service_key_path = os.path.join(
            os.path.dirname(__file__), "../../serviceAccountKey.json"
        )

        if not firebase_admin._apps:
            cred = credentials.Certificate(_service_key_path)
            firebase_admin.initialize_app(cred, {"storageBucket": STORAGE_BUCKET})

        db = firestore.client()
        bucket = storage.bucket()
        _firebase_available = True
    except Exception as e:
        logger.warning(f"Firebase not available: {e}")
else:
    logger.debug(
        "FIREBASE_STORAGE_BUCKET not set; Firebase features disabled."
    )


def _require_firebase():
    if not _firebase_available:
        raise RuntimeError(
            "Firebase is not configured. Set FIREBASE_STORAGE_BUCKET and "
            "provide a serviceAccountKey.json to use Firebase features."
        )


# Upload a file to Cloud Storage and return its public URL
def upload_file_to_storage(local_path: str, remote_filename: str) -> str:
    _require_firebase()
    try:
        logger.info(
            Fore.YELLOW
            + f"📤 Uploading file to Firebase Storage: {local_path} → outputs/{remote_filename}"
        )
        blob = bucket.blob(f"outputs/{remote_filename}")
        blob.upload_from_filename(local_path)
        blob.make_public()
        logger.info(Fore.GREEN + f"✅ Upload successful: {blob.public_url}")
        return blob.public_url
    except Exception as e:
        logger.error(Fore.RED + f"❌ Upload failed: {e}")
        raise


# Save realization metadata to Firestore
def save_realization_metadata(realization_data: dict) -> str:
    _require_firebase()
    try:
        logger.info(Fore.YELLOW + "📝 Saving realization metadata to Firestore...")
        doc_ref = db.collection(COLLECTION_ID).document()
        realization_data["created_at"] = datetime.now(timezone.utc).isoformat()
        doc_ref.set(realization_data)
        logger.info(Fore.GREEN + f"✅ Metadata saved. Document ID: {doc_ref.id}")
        return doc_ref.id
    except Exception as e:
        logger.error(Fore.RED + f"❌ Firestore write failed: {e}")
        raise


# Fetch all realizations from Firestore
def fetch_all_realizations() -> list[dict]:
    _require_firebase()
    try:
        logger.info(Fore.YELLOW + "📥 Fetching all realizations from Firestore...")
        docs = db.collection(COLLECTION_ID).stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            results.append(data)
        logger.info(Fore.GREEN + f"✅ Retrieved {len(results)} realizations.")
        return results
    except Exception as e:
        logger.error(Fore.RED + f"❌ Failed to fetch realizations: {e}")
        raise
