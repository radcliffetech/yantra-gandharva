import json
import logging
from datetime import datetime
from pathlib import Path

from colorama import Fore

from engines import EngineType
from genres.jazz.engines import get_jazz_engine
from genres.jazz.tasks import generate

logger = logging.getLogger(__name__)


def handle_lead_sheet(args):
    logger.info(Fore.CYAN + f"\n🎼 Creating MusicXML from {args.input}...")
    Path("generated/musicxml").mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    args.output = f"generated/musicxml/lead_sheet_{timestamp}.musicxml"
    generate.generate_jazz_lead_sheet(args.input, args.output)
    logger.info(Fore.YELLOW + f"\n💾 MusicXML saved to {args.output}")


def handle_generate_lead_sheet(args):
    """Generate a jazz lead sheet from a prompt using the selected engine."""
    engine_type = EngineType(getattr(args, "engine", "llm"))
    engine = get_jazz_engine(engine_type)

    logger.info(Fore.CYAN + "\n🎵 Generating jazz lead sheet...")
    lead_sheet = engine.generate_jazz_lead_sheet(args.prompt)

    # Determine output path
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    if args.output:
        json_path = Path(args.output)
    else:
        Path("generated/json").mkdir(parents=True, exist_ok=True)
        json_path = Path(f"generated/json/lead_sheet_{timestamp}.json")

    # Write JSON
    with open(json_path, "w") as f:
        json.dump(lead_sheet, f, indent=2)
    logger.info(Fore.YELLOW + f"\n💾 Lead sheet JSON saved to {json_path}")

    # Also export to MusicXML
    from genres.jazz.tasks.export import export_lead_sheet

    Path("generated/musicxml").mkdir(parents=True, exist_ok=True)
    xml_path = json_path.with_suffix(".musicxml")
    export_lead_sheet(str(json_path), str(xml_path))
    logger.info(Fore.YELLOW + f"🎼 MusicXML saved to {xml_path}")


handler_map = {
    "lead-sheet": handle_lead_sheet,
    "generate-lead-sheet": handle_generate_lead_sheet,
}
