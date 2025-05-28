import json
import logging
import os

from colorama import Fore

logger = logging.getLogger(__name__)

from lib.firebase_utils import (
    fetch_all_realizations,
    save_realization_metadata,
    upload_file_to_storage,
)


# === LIST REALIZATIONS HANDLER ===
def handle_list_realizations(args):
    logger.info(Fore.CYAN + "\n📚 Listing all realizations from Firebase...")
    realizations = fetch_all_realizations()
    for r in realizations:
        logger.info(
            Fore.YELLOW
            + f"- {r.get('id')} | {r.get('prompt', 'No prompt')} | {r.get('created_at')}"
        )


def handle_push_chain(args):
    logger.info(
        Fore.CYAN + f"\n☁️ Uploading realization chain at {args.input} to Firebase..."
    )

    metadata_path = os.path.join(args.input, "metadata.json")
    if not os.path.exists(metadata_path):
        logger.error(Fore.RED + "❌ metadata.json not found in specified directory.")
        return

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    musicxml_path = os.path.join(args.input, metadata["files"]["musicxml"])
    if not os.path.exists(musicxml_path):
        logger.error(Fore.RED + f"❌ MusicXML file not found at {musicxml_path}")
        return

    # Upload MusicXML file
    logger.info(Fore.YELLOW + f"📤 Uploading MusicXML to Firebase Storage...")
    remote_filename = os.path.basename(musicxml_path)
    public_url = upload_file_to_storage(musicxml_path, remote_filename)
    logger.info(Fore.GREEN + f"✅ Uploaded: {public_url}")

    # Add public_url to metadata and push Firestore doc
    metadata["exported_musicxml_url"] = public_url
    doc_id = save_realization_metadata(metadata)
    logger.info(Fore.GREEN + f"✅ Metadata saved to Firestore. Document ID: {doc_id}")


# === HANDLER MAP ===
# Dispatch map for all CLI commands to their corresponding handler functions.

handler_map = {
    "push-chain": handle_push_chain,
    "list-realizations": handle_list_realizations,
}
