import json
import os
from datetime import datetime

from colorama import Fore, Style

from generate import figured_bass, jazz_lead_sheet
from llm.client import call_llm
from llm.tasks import generate_score, realize_figured_bass


def handle_llm_generate(args):
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


def handle_generate_lead_sheet(args):
    print(Fore.CYAN + f"\n🎼 Creating MusicXML from {args.input}...")
    if not args.output:
        os.makedirs("generated/musicxml", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        args.output = f"generated/musicxml/lead_sheet_{timestamp}.musicxml"
    jazz_lead_sheet.create_lead_sheet(args.input, args.output)
    print(Fore.YELLOW + f"\n💾 MusicXML saved to {args.output}")


def handle_generate_figured_bass(args):
    print(Fore.CYAN + f"\n🎼 Creating figured bass MusicXML from {args.input}...")
    if not args.output:
        os.makedirs("generated/musicxml", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        args.output = f"generated/musicxml/figured_bass_{timestamp}.musicxml"
    figured_bass.create_figured_bass_realization(args.input, args.output)
    print(Fore.YELLOW + f"\n💾 MusicXML saved to {args.output}")


def handle_chain_figured_bass(args):
    print(Fore.CYAN + f"\n🔗 Realizing and rendering figured bass from prompt...")
    result = realize_figured_bass.generate_figured_bass_realization(
        args.prompt, call_llm
    )
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # Save JSON
    os.makedirs("generated/json", exist_ok=True)
    json_path = f"generated/json/figured_{timestamp}.json"
    with open(json_path, "w") as f:
        f.write(json.dumps(result, indent=2))

    # Save MusicXML
    os.makedirs("generated/musicxml", exist_ok=True)
    xml_path = f"generated/musicxml/figured_{timestamp}.musicxml"
    figured_bass.create_figured_bass_realization(json_path, xml_path)

    print(Fore.YELLOW + f"\n💾 JSON saved to {json_path}")
    print(Fore.YELLOW + f"🎼 MusicXML saved to {xml_path}")


def handle_realize_figured_bass(args):
    print(Fore.CYAN + f"\n🎼 Realizing figured bass from prompt...")
    result = realize_figured_bass_from_prompt(args.prompt, call_llm)
    output_json = json.dumps(result, indent=2)
    print(Fore.GREEN + "\n✅ Realized figured bass:\n" + Style.RESET_ALL + output_json)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        os.makedirs("generated", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = f"generated/realized_figured_bass_{timestamp}.json"

    with open(output_path, "w") as f:
        f.write(output_json)
    print(Fore.YELLOW + f"\n💾 Saved to {output_path}")
