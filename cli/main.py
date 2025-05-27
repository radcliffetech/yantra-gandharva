import os
import sys

# Ensure src/ is in sys.path for imports
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
import argparse
import json
from datetime import datetime

from colorama import Fore, Style, init

from generate import figured_bass, jazz_lead_sheet
from llm import generate_score

init(autoreset=True)


def main():
    parser = argparse.ArgumentParser(description="Yantra-Gandharva Score Generator")
    subparsers = parser.add_subparsers(dest="command")

    # LLM generation command
    gen_parser = subparsers.add_parser(
        "llm-generate", help="Generate score JSON using LLM"
    )
    gen_parser.add_argument(
        "type", choices=["jazz", "figured"], help="Score type to generate"
    )
    gen_parser.add_argument("prompt", help="Natural language prompt to feed the model")
    gen_parser.add_argument(
        "--output", "-o", help="Path to save the generated JSON (optional)"
    )

    # MusicXML generation command
    lead_parser = subparsers.add_parser(
        "lead-sheet", help="Generate MusicXML from a lead sheet JSON file"
    )
    lead_parser.add_argument("input", help="Path to input JSON file")
    lead_parser.add_argument(
        "output", nargs="?", help="Path to output MusicXML file (optional)"
    )

    # Figured bass MusicXML generation command
    fb_parser = subparsers.add_parser(
        "figured-bass", help="Generate MusicXML from a figured bass JSON file"
    )
    fb_parser.add_argument("input", help="Path to input JSON file")
    fb_parser.add_argument(
        "output", nargs="?", help="Path to output MusicXML file (optional)"
    )

    # LLM figured bass realization command
    rfb_parser = subparsers.add_parser(
        "realize-figured-bass", help="Use LLM to realize a figured bass from a prompt"
    )
    rfb_parser.add_argument(
        "prompt", help="Natural language prompt describing the figured bass progression"
    )
    rfb_parser.add_argument(
        "--output", "-o", help="Path to save the generated JSON (optional)"
    )

    args = parser.parse_args()

    if args.command == "llm-generate":
        print(Fore.CYAN + f"\n🎼 Generating {args.type} score from prompt...")
        score_data = generate_score.prompt_to_json(args.prompt, args.type)
        output_json = json.dumps(score_data, indent=2)
        print(Fore.GREEN + "\n✅ Score data:\n" + Style.RESET_ALL + output_json)

        # Determine output path
        if args.output:
            output_path = args.output
        else:
            os.makedirs("generated", exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            output_path = f"generated/{args.type}_{timestamp}.json"

        with open(output_path, "w") as f:
            f.write(output_json)
        print(Fore.YELLOW + f"\n💾 Saved to {output_path}")

    elif args.command == "lead-sheet":
        print(Fore.CYAN + f"\n🎼 Creating MusicXML from {args.input}...")
        if not args.output:
            os.makedirs("generated/musicxml", exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            args.output = f"generated/musicxml/lead_sheet_{timestamp}.musicxml"
        jazz_lead_sheet.create_lead_sheet(args.input, args.output)
        print(Fore.YELLOW + f"\n💾 MusicXML saved to {args.output}")

    elif args.command == "figured-bass":
        print(Fore.CYAN + f"\n🎼 Creating figured bass MusicXML from {args.input}...")
        if not args.output:
            os.makedirs("generated/musicxml", exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            args.output = f"generated/musicxml/figured_bass_{timestamp}.musicxml"
        figured_bass.create_figured_bass_realization(args.input, args.output)
        print(Fore.YELLOW + f"\n💾 MusicXML saved to {args.output}")

    elif args.command == "realize-figured-bass":
        print(Fore.CYAN + f"\n🎼 Realizing figured bass from prompt...")
        result = generate_score.realize_figured_bass_from_prompt(args.prompt)
        output_json = json.dumps(result, indent=2)

        if args.output:
            output_path = args.output
        else:
            os.makedirs("generated/json", exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            output_path = f"generated/json/figured_{timestamp}.json"

        with open(output_path, "w") as f:
            f.write(output_json)
        print(Fore.YELLOW + f"\n💾 Realization saved to {output_path}")


if __name__ == "__main__":
    main()
