import logging
import os
from datetime import datetime

from colorama import Fore

logger = logging.getLogger(__name__)

from genres.jazz.tasks import generate


def handle_lead_sheet(args):
    logger.info(Fore.CYAN + f"\n🎼 Creating MusicXML from {args.input}...")
    os.makedirs("generated/musicxml", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    args.output = f"generated/musicxml/lead_sheet_{timestamp}.musicxml"
    generate.generate_jazz_lead_sheet(args.input, args.output)
    logger.info(Fore.YELLOW + f"\n💾 MusicXML saved to {args.output}")


handler_map = {
    "lead-sheet": handle_lead_sheet,
}
