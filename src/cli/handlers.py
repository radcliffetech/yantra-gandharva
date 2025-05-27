# === GENERATE AND REVIEW PARTIMENTO HANDLER ===
# Handler to generate, review, and export a partimento (without realization)


def handle_generate_and_review_partimento(args):
    print(Fore.CYAN + f"\n🎼 Generating and reviewing partimento...")

    # Step 1: Generate partimento
    partimento_data = generate.generate_partimento(args.prompt, call_llm)
    partimento_output = {
        **generate_metadata(args.prompt, "generate-partimento"),
        "data": partimento_data,
    }

    # Determine base filename
    if args.output:
        base = args.output
        # If endswith .json, strip for base
        if base.endswith(".json"):
            base = base[:-5]
    else:
        os.makedirs("generated/json", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        base = f"generated/json/partimento_{timestamp}"

    json_path = f"{base}.json"
    with open(json_path, "w") as f:
        f.write(json.dumps(partimento_output, indent=2))
    print(Fore.YELLOW + f"\n💾 Partimento saved to {json_path}")

    # Step 2: Review partimento
    print(Fore.CYAN + f"\n🔍 Reviewing partimento...")
    review_json = review_partimento(json_path, call_llm)
    review_data = json.loads(review_json)

    os.makedirs("generated/review", exist_ok=True)
    # Use same timestamp as above if possible
    if "timestamp" not in locals():
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    review_path = f"generated/review/review_partimento_{timestamp}.json"
    with open(review_path, "w") as f:
        f.write(
            json.dumps(
                {
                    **generate_metadata(json_path, "review-partimento"),
                    "data": review_data,
                },
                indent=2,
            )
        )
    print(Fore.GREEN + f"\n✅ Partimento review saved to {review_path}")
    print(Fore.YELLOW + "\n💬 Review Summary:")
    print(Fore.GREEN + review_data.get("message", "No review message provided."))

    # Step 3: Export to MusicXML
    print(Fore.CYAN + f"\n🎼 Exporting partimento to MusicXML...")
    os.makedirs("generated/musicxml", exist_ok=True)
    xml_path = f"generated/musicxml/{os.path.basename(base)}.musicxml"
    export_partimento_to_musicxml(json_path, xml_path)
    print(Fore.YELLOW + f"\n✅ MusicXML saved to {xml_path}")


import json
import os
from datetime import datetime

from colorama import Fore, Style

from generate.partimento.export import (
    export_partimento_to_musicxml,
    export_realized_partimento_to_midi,
    export_realized_partimento_to_musicxml,
)
from llm.client import call_llm
from llm.tasks.jazz import generate
from llm.tasks.partimento import generate
from llm.tasks.partimento.realize import realize_partimento_satb
from llm.tasks.partimento.review import review_partimento, review_realized_score
from utils.json_utils import apply_patch
from utils.metadata_utils import generate_metadata
from utils.musicxml_tools import load_musicxml

# === PARTIMENTO GENERATION AND EXPORT ===
# Handles generating partimenti, realizing them, and exporting to MusicXML and MIDI formats.


def handle_partimento(args):
    print(Fore.CYAN + f"\n🎼 Generating partimento bass line from prompt...")
    partimento_data = generate.generate_partimento(args.prompt, call_llm)
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
    print(
        Fore.CYAN
        + f"\n🔗 Generating → Reviewing → Realizing → Reviewing → Exporting partimento..."
    )

    print(Fore.CYAN + f"\n🔗 1. Generating Partimento...")

    # Generate partimento
    partimento_data = generate.generate_partimento(args.prompt, call_llm)
    partimento_output = {
        **generate_metadata(args.prompt, "generate-partimento"),
        "data": partimento_data,
    }

    # File paths
    if args.output:
        base = args.output
    else:
        os.makedirs("generated/json", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        base = f"generated/json/partimento_{timestamp}"

    json_path = f"{base}.json"
    with open(json_path, "w") as f:
        f.write(json.dumps(partimento_output, indent=2))
    print(Fore.YELLOW + f"\n💾 Partimento saved to {json_path}")

    # Review partimento
    print(Fore.CYAN + f"\n🔗 2. Reviewing partimento...")
    review_json = review_partimento(json_path, call_llm)
    review_data = json.loads(review_json)
    review_dir = "generated/review"
    os.makedirs(review_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    review_partimento_path = f"{review_dir}/review_partimento_{timestamp}.json"
    with open(review_partimento_path, "w") as f:
        f.write(
            json.dumps(
                {
                    **generate_metadata(json_path, "review-partimento"),
                    "data": review_data,
                },
                indent=2,
            )
        )
    print(Fore.YELLOW + "\n💬 Partimento Review:")
    print(Fore.GREEN + review_data.get("message", "No review message provided."))
    partimento_patch = review_data.get("suggested_patch")
    if partimento_patch:
        partimento_data = apply_patch(partimento_data, partimento_patch)
        partimento_output["data"] = partimento_data
        with open(json_path, "w") as f:
            f.write(json.dumps(partimento_output, indent=2))
        print(
            Fore.YELLOW + f"\n✅ Patch applied. Updated partimento saved to {json_path}"
        )

    # Realize partimento
    print(Fore.CYAN + f"\n🔗 3.Realizing partimento...")
    realization = realize_partimento_satb(partimento_data, call_llm)
    realization_output = {
        **generate_metadata(args.prompt, "realize-partimento"),
        "data": realization,
    }
    realized_path = f"{base}_realized.json"
    with open(realized_path, "w") as f:
        f.write(json.dumps(realization_output, indent=2))
    print(Fore.YELLOW + f"\n🎶 Realization saved to {realized_path}")

    # Review realization
    print(Fore.CYAN + f"\n🔗 4.Reviewing realization...")
    review_json = review_realized_score(realized_path, call_llm)
    review_data = json.loads(review_json)
    review_realization_path = f"{review_dir}/review_realization_{timestamp}.json"
    with open(review_realization_path, "w") as f:
        f.write(
            json.dumps(
                {
                    **generate_metadata(realized_path, "review-realization"),
                    "data": review_data,
                },
                indent=2,
            )
        )
    print(Fore.YELLOW + "\n💬 Realization Review:")
    print(Fore.GREEN + review_data.get("message", "No review message provided."))
    realization_patch = review_data.get("suggested_patch")
    if realization_patch:
        realization = apply_patch(realization, realization_patch)
        realization_output["data"] = realization
        with open(realized_path, "w") as f:
            f.write(json.dumps(realization_output, indent=2))
        print(
            Fore.YELLOW
            + f"\n✅ Patch applied. Updated realization saved to {realized_path}"
        )

    print(Fore.CYAN + f"\n🔗 5.Exporting realization...")
    # Export to MusicXML
    os.makedirs("generated/musicxml", exist_ok=True)
    xml_path = f"generated/musicxml/{os.path.basename(base)}_realized.musicxml"
    export_realized_partimento_to_musicxml(realized_path, xml_path)
    print(Fore.YELLOW + f"🎼 MusicXML saved to {xml_path}")
    # Export to MIDI
    os.makedirs("generated/midi", exist_ok=True)
    midi_path = f"generated/midi/{os.path.basename(base)}_realized.mid"
    export_realized_partimento_to_midi(realized_path, midi_path)
    print(Fore.YELLOW + f"🎧 MIDI saved to {midi_path}")

    print(
        Fore.GREEN
        + "\n✅ Partimento generation, realization, review, and export completed successfully!"
    )


def handle_realize_partimento(args):
    print(Fore.CYAN + f"\n🎼 Realizing partimento from {args.input}...")
    realized_data = generate.realize_partimento_satb(args.input, call_llm)
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


# === JAZZ/LEAD SHEET ===
# Handler for creating lead sheets from JSON input.


def handle_lead_sheet(args):
    print(Fore.CYAN + f"\n🎼 Creating MusicXML from {args.input}...")
    os.makedirs("generated/musicxml", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    args.output = f"generated/musicxml/lead_sheet_{timestamp}.musicxml"
    generate.generate_jazz_lead_sheet(args.input, args.output)
    print(Fore.YELLOW + f"\n💾 MusicXML saved to {args.output}")


# === REVIEW AND REVISE ===
# Includes functions to review partimenti and SATB realizations, and to apply patches.


def handle_review_score(args):
    print(Fore.CYAN + f"\n🔍 Reviewing realized partimento from {args.input}...")
    review_json = review_realized_score(args.input, call_llm)
    review_data = json.loads(review_json)

    from utils.metadata_utils import generate_metadata

    metadata = generate_metadata(args.input, "review-partimento")

    output = {**metadata, "data": review_data}

    # Save to JSON file
    os.makedirs("generated/review", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_path = f"generated/review/review_{timestamp}.json"

    with open(output_path, "w") as f:
        f.write(json.dumps(output, indent=2))

    print(Fore.GREEN + "\n✅ Review saved to", output_path)
    print(Fore.YELLOW + "\n💬 Summary:")
    print(Fore.GREEN + review_data.get("message", "No review message provided."))

    strengths = review_data.get("strengths", [])
    if strengths:
        print(Fore.YELLOW + "\nStrengths:")
        for s in strengths:
            print(Fore.YELLOW + f"- {s}")

    issues = review_data.get("issues", [])
    if issues:
        print(Fore.RED + "\nIssues:")
        for i in issues:
            print(Fore.RED + f"- {i}")


def handle_review_partimento(args):
    print(Fore.CYAN + f"\n🔍 Reviewing partimento from {args.input}...")
    review_json = review_partimento(args.input, call_llm)
    review_data = json.loads(review_json)

    from utils.metadata_utils import generate_metadata

    metadata = generate_metadata(args.input, "review-partimento")

    output = {**metadata, "data": review_data}

    # Save to JSON file
    os.makedirs("generated/review", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_path = f"generated/review/review_{timestamp}.json"

    with open(output_path, "w") as f:
        f.write(json.dumps(output, indent=2))

    print(Fore.GREEN + "\n✅ Review saved to", output_path)
    print(Fore.YELLOW + "\n💬 Summary:")
    print(Fore.GREEN + review_data.get("message", "No review message provided."))

    strengths = review_data.get("strengths", [])
    if strengths:
        print(Fore.YELLOW + "\nStrengths:")
        for s in strengths:
            print(Fore.YELLOW + f"- {s}")

    issues = review_data.get("issues", [])
    if issues:
        print(Fore.RED + "\nIssues:")
        for i in issues:
            print(Fore.RED + f"- {i}")


def handle_revise_score(args):
    print(Fore.CYAN + f"\n🔧 Revising realization based on patch...")

    with open(args.input, "r") as f:
        original = json.load(f)

    with open(args.patch, "r") as f:
        review = json.load(f)

    patch = review.get("data", {}).get("suggested_patch")
    if not patch:
        print(Fore.RED + "❌ No suggested_patch found in review file.")
        return

    updated_data = apply_patch(original["data"], patch)
    output = {
        **generate_metadata(args.input, "revise-partimento"),
        "data": updated_data,
    }

    os.makedirs("generated/json", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_path = args.output or f"generated/json/revised_partimento_{timestamp}.json"

    with open(output_path, "w") as f:
        f.write(json.dumps(output, indent=2))

    print(Fore.YELLOW + f"\n✅ Revised realization saved to {output_path}")


# === UTILITY/INSPECTION ===
# CLI tool for inspecting MusicXML files.


def handle_inspect_musicxml(args):
    from utils.musicxml_tools import print_score_summary

    print(Fore.CYAN + f"\n🔍 Inspecting MusicXML file: {args.input}...")

    # load the MusicXML file

    score = load_musicxml(args.input)
    if not score:
        print(Fore.RED + "❌ Failed to load MusicXML file.")
        return
    print(Fore.GREEN + "✅ Successfully loaded MusicXML file.")
    print_score_summary(score)


# === HANDLER MAP ===
# Dispatch map for all CLI commands to their corresponding handler functions.

handler_map = {
    "lead-sheet": handle_lead_sheet,
    "generate-partimento": handle_partimento,
    "chain-partimento": handle_chain_partimento,
    "export-partimento-to-musicxml": handle_export_partimento_to_musicxml,
    "export-realized-partimento-to-musicxml": handle_export_realized_partimento_to_musicxml,
    "realize-partimento": handle_realize_partimento,
    "inspect-musicxml": handle_inspect_musicxml,
    "review-score": handle_review_score,
    "review-partimento": handle_review_partimento,
    "revise-score": handle_revise_score,
    "generate-and-review-partimento": handle_generate_and_review_partimento,
}
