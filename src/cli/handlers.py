import json
import os
from datetime import datetime

from colorama import Fore, Style

from generate.partimento import (
    export_partimento_to_musicxml,
    export_realized_partimento_to_musicxml,
)
from llm.client import call_llm
from llm.tasks import generate_jazz, generate_partimento
from llm.tasks.generate_partimento import realize_partimento_satb
from utils.metadata_utils import generate_metadata


def handle_lead_sheet(args):
    print(Fore.CYAN + f"\n🎼 Creating MusicXML from {args.input}...")
    if not args.output:
        os.makedirs("generated/musicxml", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        args.output = f"generated/musicxml/lead_sheet_{timestamp}.musicxml"
    generate_jazz.generate_jazz_lead_sheet(args.input, args.output)
    print(Fore.YELLOW + f"\n💾 MusicXML saved to {args.output}")


def handle_partimento(args):
    print(Fore.CYAN + f"\n🎼 Generating partimento bass line from prompt...")
    partimento_data = generate_partimento.generate_partimento(args.prompt, call_llm)
    output = {
        **generate_metadata(args.prompt, "generate-partimento"),
        "data": partimento_data,
    }
    output_json = json.dumps(output, indent=2)
    print(Fore.GREEN + "\n✅ Generated partimento:\n" + Style.RESET_ALL + output_json)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        os.makedirs("generated/json", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = f"generated/json/partimento_{timestamp}.json"

    with open(output_path, "w") as f:
        f.write(output_json)
    print(Fore.YELLOW + f"\n💾 Saved to {output_path}")

    # Export to MusicXML
    xml_path = output_path.replace(".json", ".musicxml")
    os.makedirs("generated/musicxml", exist_ok=True)
    export_partimento_to_musicxml(output_path, xml_path)


# Chain partimento handler
def handle_chain_partimento(args):
    print(Fore.CYAN + f"\n🔗 Generating → Realizing → Exporting partimento...")

    # Generate partimento
    partimento_data = generate_partimento.generate_partimento(args.prompt, call_llm)
    partimento_output = {
        **generate_metadata(args.prompt, "generate-partimento"),
        "data": partimento_data,
    }

    # Determine base name
    if args.output:
        base = args.output
    else:
        os.makedirs("generated/json", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        base = f"generated/json/partimento_{timestamp}"

    json_path = f"{base}.json"
    realized_path = f"{base}_realized.json"
    xml_path = f"generated/musicxml/{os.path.basename(base)}_realized.musicxml"

    # Write partimento JSON
    with open(json_path, "w") as f:
        f.write(json.dumps(partimento_output, indent=2))
    print(Fore.YELLOW + f"\n💾 JSON saved to {json_path}")

    # Realize partimento
    realization = realize_partimento_satb(partimento_output, call_llm)
    realization_output = {
        **generate_metadata(args.prompt, "realize-partimento"),
        "data": realization,
    }
    with open(realized_path, "w") as f:
        f.write(json.dumps(realization_output, indent=2))
    print(Fore.YELLOW + f"🎶 Realization saved to {realized_path}")

    # Export to MusicXML
    export_realized_partimento_to_musicxml(realized_path, xml_path)
    print(Fore.YELLOW + f"🎼 MusicXML saved to {xml_path}")


def handle_export_partimento_to_musicxml(args):
    print(
        Fore.CYAN + f"\n🎼 Exporting partimento JSON to MusicXML from {args.input}..."
    )
    if not args.output:
        os.makedirs("generated/musicxml", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        args.output = f"generated/musicxml/partimento_{timestamp}.musicxml"
    export_partimento_to_musicxml(args.input, args.output)
    print(Fore.YELLOW + f"\n💾 MusicXML saved to {args.output}")


def handle_realize_partimento(args):
    print(Fore.CYAN + f"\n🎼 Realizing partimento from {args.input}...")
    realized_data = generate_partimento.realize_partimento_satb(args.input, call_llm)
    output_json = json.dumps(realized_data, indent=2)
    print(Fore.GREEN + "\n✅ Realized partimento:\n" + Style.RESET_ALL + output_json)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        os.makedirs("generated/json", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = f"generated/json/realized_partimento_{timestamp}.json"

    with open(output_path, "w") as f:
        f.write(output_json)
    print(Fore.YELLOW + f"\n💾 Saved to {output_path}")


def handle_export_realized_partimento_to_musicxml(args):
    print(
        Fore.CYAN
        + f"\n🎼 Exporting realized partimento JSON to MusicXML from {args.input}..."
    )
    if not args.output:
        os.makedirs("generated/musicxml", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        args.output = f"generated/musicxml/realized_partimento_{timestamp}.musicxml"
    export_realized_partimento_to_musicxml(args.input, args.output)
    print(Fore.YELLOW + f"\n💾 MusicXML saved to {args.output}")


handler_map = {
    "lead-sheet": handle_lead_sheet,
    "generate-partimento": handle_partimento,
    "chain-partimento": handle_chain_partimento,
    "export-partimento-to-musicxml": handle_export_partimento_to_musicxml,
    "export-realized-partimento-to-musicxml": handle_export_realized_partimento_to_musicxml,
    "realize-partimento": handle_realize_partimento,
}
