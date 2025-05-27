from utils.playback import open_file_if_possible


# === DESCRIBE CHAIN HANDLER ===
# Prints chain metadata in a readable way
def handle_describe_chain(args):
    print(Fore.CYAN + f"\n📦 Describing chain: {args.input}")
    meta_path = os.path.join(args.input, "metadata.json")
    if not os.path.exists(meta_path):
        print(Fore.RED + "❌ No metadata.json found in the specified directory.")
        return

    with open(meta_path, "r") as f:
        metadata = json.load(f)

    print(Fore.GREEN + "\n📄 Metadata:")
    for key in ["id", "created_at", "mode", "prompt", "version"]:
        print(Fore.YELLOW + f"{key}: {metadata.get(key)}")

    print(Fore.YELLOW + "\n📁 Files:")
    for k, v in metadata.get("files", {}).items():
        print(Fore.YELLOW + f"  {k}: {v}")

    if "patched" in metadata:
        print(Fore.YELLOW + "\n🩹 Patches Applied:")
        for k, v in metadata["patched"].items():
            status = "✅" if v else "—"
            print(Fore.YELLOW + f"  {k}: {status}")


import json
import os
import subprocess
import sys
import uuid
from datetime import datetime

from colorama import Fore, Style

from generate.partimento.export import (
    export_partimento_to_midi,
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

# === GENERATE AND REVIEW PARTIMENTO HANDLER ===
# Handler to generate, review, and export a partimento (without realization)


def handle_chain_partimento_only(args):
    print(Fore.CYAN + f"\n🎼 Generating and reviewing partimento...")

    # Create a unified output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    chain_dir = args.output or f"generated/chains/partimento_{timestamp}"
    os.makedirs(chain_dir, exist_ok=True)

    base_json_path = os.path.join(chain_dir, "partimento.json")
    xml_path = os.path.join(chain_dir, "partimento.musicxml")

    # Step 1: Generate partimento
    partimento_data = generate.generate_partimento(args.prompt, call_llm)
    partimento_output = {
        **generate_metadata(args.prompt, "generate-partimento"),
        "data": partimento_data,
    }
    with open(base_json_path, "w") as f:
        f.write(json.dumps(partimento_output, indent=2))
    print(Fore.YELLOW + f"\n💾 Partimento saved to {base_json_path}")

    # Step 2: Review partimento with iteration support, storing each version
    iterations = getattr(args, "iterations", 1)
    current_json_path = base_json_path
    partimento_versions = [os.path.basename(base_json_path)]
    review_versions = []
    for i in range(iterations):
        print(Fore.CYAN + f"\n🔍 Reviewing partimento (pass {i+1})...")
        review_json = review_partimento(current_json_path, call_llm)
        review_data = json.loads(review_json)

        iter_review_path = os.path.join(chain_dir, f"review_partimento_{i+1}.json")
        with open(iter_review_path, "w") as f:
            f.write(
                json.dumps(
                    {
                        **generate_metadata(
                            current_json_path, f"review-partimento-pass-{i+1}"
                        ),
                        "data": review_data,
                    },
                    indent=2,
                )
            )
        print(Fore.GREEN + f"\n✅ Review saved to {iter_review_path}")
        print(Fore.YELLOW + "\n💬 Review Summary:")
        print(Fore.GREEN + review_data.get("message", "No review message provided."))
        review_versions.append(os.path.basename(iter_review_path))

        patch = review_data.get("suggested_patch")
        if not patch:
            print(Fore.YELLOW + "No patch suggested. Stopping review loop.")
            break

        # Load current version and apply patch
        with open(current_json_path, "r") as f:
            working_data = json.load(f)
        updated = apply_patch(working_data["data"], patch)

        # Write updated file with numeric suffix
        new_json_path = os.path.join(chain_dir, f"partimento_{i+1}.json")
        working_data["data"] = updated
        with open(new_json_path, "w") as f:
            json.dump(working_data, f, indent=2)
        print(Fore.YELLOW + f"\n✅ Patch applied and saved to {new_json_path}")
        current_json_path = new_json_path
        partimento_versions.append(os.path.basename(new_json_path))

    # Step 3: Export to MusicXML (use last version)
    print(Fore.CYAN + f"\n🎼 Exporting final partimento to MusicXML...")
    export_partimento_to_musicxml(current_json_path, xml_path)
    print(Fore.YELLOW + f"\n✅ MusicXML saved to {xml_path}")
    # Export to MIDI
    midi_path = os.path.join(chain_dir, "partimento.mid")
    export_partimento_to_midi(current_json_path, midi_path)
    print(Fore.YELLOW + f"🎧 MIDI saved to {midi_path}")
    # Write metadata
    meta_path = os.path.join(chain_dir, "metadata.json")
    files_dict = {
        "partimento_versions": partimento_versions,
        "review_versions": review_versions,
        "musicxml": os.path.basename(xml_path),
    }
    with open(meta_path, "w") as f:
        json.dump(
            {
                "id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat() + "Z",
                "mode": "generate-and-review-partimento",
                "prompt": args.prompt,
                "files": files_dict,
                "version": "0.1.0",
            },
            f,
            indent=2,
        )
    print(Fore.GREEN + f"\n📦 Metadata saved to {meta_path}")

    print(Fore.GREEN + "\n📊 Summary:")
    print(Fore.YELLOW + f"📄 Chain ID: {os.path.basename(chain_dir)}")
    print(Fore.YELLOW + f"📁 Output dir: {chain_dir}")
    print(Fore.YELLOW + f"🎼 Prompt style: {args.prompt}")
    print(Fore.YELLOW + f"🎧 Audio preview: {ogg_path}")
    print(Fore.YELLOW + f"📝 Iterations: {args.iterations}")
    print(Fore.CYAN + f"\n🔗 Complete. Data is stored in {chain_dir}")

    ogg_path = midi_path.replace(".mid", ".ogg")
    print(Fore.CYAN + f"\n🎧 Writing OGG file: {ogg_path}")
    if not os.path.exists(midi_path):
        print(Fore.RED + "❌ MIDI file not found.")
        open_file_if_possible(ogg_path)
        return

    # Try Timidity first
    try:
        subprocess.run(["timidity", midi_path], check=True)
        return
    except FileNotFoundError:
        print(
            Fore.YELLOW
            + "⚠️  Timidity not found. Falling back to system default player..."
        )


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
def handle_chain_partimento_realization(args):
    print(
        Fore.CYAN
        + f"\n🔗 Generating → Reviewing → Realizing → Reviewing → Exporting partimento..."
    )

    print(Fore.CYAN + f"\n🔗 1. Generating Partimento...")

    # Step 1: Setup output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    if args.output:
        chain_dir = args.output
    else:
        chain_dir = f"generated/chains/partimento_{timestamp}"
    os.makedirs(chain_dir, exist_ok=True)

    json_path = f"{chain_dir}/partimento.json"
    realized_path = f"{chain_dir}/realized.json"
    xml_path = f"{chain_dir}/realized.musicxml"
    midi_path = f"{chain_dir}/realized.mid"

    # Generate partimento
    partimento_data = generate.generate_partimento(args.prompt, call_llm)
    partimento_output = {
        **generate_metadata(args.prompt, "generate-partimento"),
        "data": partimento_data,
    }
    with open(json_path, "w") as f:
        f.write(json.dumps(partimento_output, indent=2))
    print(Fore.YELLOW + f"\n💾 Partimento saved to {json_path}")

    # === Multiple review loops for partimento (before realization) ===
    partimento_versions = [os.path.basename(json_path)]
    review_partimento_versions = []
    current_partimento_path = json_path
    current_partimento_data = partimento_data
    partimento_patch = None
    for i in range(args.iterations):
        print(Fore.CYAN + f"\n🔍 Reviewing partimento (pass {i+1})...")
        review_json = review_partimento(current_partimento_path, call_llm)
        review_data = json.loads(review_json)
        part_review_path = os.path.join(chain_dir, f"review_partimento_{i+1}.json")
        with open(part_review_path, "w") as f:
            f.write(
                json.dumps(
                    {
                        **generate_metadata(
                            current_partimento_path, f"review-partimento-pass-{i+1}"
                        ),
                        "data": review_data,
                    },
                    indent=2,
                )
            )
        print(Fore.GREEN + f"\n✅ Review saved to {part_review_path}")
        print(Fore.YELLOW + "\n💬 Partimento Review:")
        print(Fore.GREEN + review_data.get("message", "No review message provided."))
        review_partimento_versions.append(os.path.basename(part_review_path))

        partimento_patch = review_data.get("suggested_patch")
        if not partimento_patch:
            print(Fore.YELLOW + "No patch suggested. Stopping review loop.")
            break

        # Load and apply patch
        with open(current_partimento_path, "r") as f:
            current_data = json.load(f)
        patched = apply_patch(current_data["data"], partimento_patch)

        # Write patched version
        next_partimento_path = os.path.join(chain_dir, f"partimento_{i+1}.json")
        current_data["data"] = patched
        with open(next_partimento_path, "w") as f:
            json.dump(current_data, f, indent=2)
        print(
            Fore.YELLOW
            + f"\n✅ Patch applied. Updated partimento saved to {next_partimento_path}"
        )
        current_partimento_path = next_partimento_path
        partimento_versions.append(os.path.basename(next_partimento_path))
        current_partimento_data = patched

    # After review loop, set json_path and partimento_data to last version
    json_path = current_partimento_path
    partimento_data = current_partimento_data

    # Export partimento to MIDI (for OGG export)
    midi_path = os.path.join(chain_dir, "partimento.mid")
    export_partimento_to_midi(current_partimento_path, midi_path)
    print(Fore.YELLOW + f"🎧 Partimento MIDI saved to {midi_path}")
    # Export OGG for partimento
    ogg_path = midi_path.replace(".mid", ".ogg")
    if os.path.exists(midi_path):
        try:
            subprocess.run(["timidity", midi_path, "-Ow", "-o", ogg_path], check=True)
            print(Fore.YELLOW + f"🎧 Partimento OGG audio saved to {ogg_path}")
        except FileNotFoundError:
            print(
                Fore.YELLOW
                + "⚠️  Timidity not found. Skipping partimento OGG audio export."
            )

    # Realize partimento
    print(Fore.CYAN + f"\n🔗 3.Realizing partimento...")
    realization = realize_partimento_satb(partimento_data, call_llm)
    realization_output = {
        **generate_metadata(args.prompt, "realize-partimento"),
        "data": realization,
    }
    with open(realized_path, "w") as f:
        f.write(json.dumps(realization_output, indent=2))
    print(Fore.YELLOW + f"\n🎶 Realization saved to {realized_path}")

    # === Multiple review loops for realization ===
    realization_versions = []
    last_realized_path = realized_path
    realization_patch = None
    for i in range(args.iterations):
        input_path = (
            last_realized_path
            if i == 0
            else os.path.join(chain_dir, f"realized_{i}.json")
        )
        review_path = os.path.join(chain_dir, f"review_realization_{i+1}.json")
        new_realized_path = os.path.join(chain_dir, f"realized_{i+1}.json")

        # Review
        review_json = review_realized_score(input_path, call_llm)
        review_data = json.loads(review_json)
        with open(review_path, "w") as f:
            json.dump(
                {
                    **generate_metadata(input_path, "review-realization"),
                    "data": review_data,
                },
                f,
                indent=2,
            )

        print(Fore.YELLOW + f"\n🔍 Review {i+1} completed.")
        print(Fore.GREEN + review_data.get("message", "No review message provided."))

        realization_patch = review_data.get("suggested_patch")
        if not realization_patch:
            print(Fore.YELLOW + "No patch suggested; stopping review loop.")
            break

        # Patch
        with open(input_path, "r") as f:
            current_data = json.load(f)["data"]
        updated = apply_patch(current_data, realization_patch)
        with open(new_realized_path, "w") as f:
            json.dump(
                {
                    **generate_metadata(args.prompt, f"realize-partimento-pass-{i+1}"),
                    "data": updated,
                },
                f,
                indent=2,
            )
        print(Fore.YELLOW + f"✅ Patch applied: realized_{i+1}.json")
        realization_versions.append(os.path.basename(new_realized_path))
        last_realized_path = new_realized_path

        # Export OGG audio for each version
        midi_path = os.path.join(chain_dir, f"realized_{i+1}.mid")
        # Export MIDI for this version
        export_realized_partimento_to_midi(new_realized_path, midi_path)
        ogg_path = new_realized_path.replace(".json", ".ogg")
        if os.path.exists(midi_path):
            try:
                subprocess.run(
                    ["timidity", midi_path, "-Ow", "-o", ogg_path], check=True
                )
                print(Fore.YELLOW + f"🎧 OGG audio saved to {ogg_path}")
            except FileNotFoundError:
                print(Fore.YELLOW + "⚠️  Timidity not found. Skipping OGG audio export.")

    # Export final version
    final_realized = last_realized_path if realization_versions else realized_path
    print(Fore.CYAN + f"\n🔗 5.Exporting realization...")
    # Export to MusicXML
    export_realized_partimento_to_musicxml(final_realized, xml_path)
    print(Fore.YELLOW + f"🎼 MusicXML saved to {xml_path}")
    # Export to MIDI
    export_realized_partimento_to_midi(final_realized, midi_path)
    print(Fore.YELLOW + f"🎧 MIDI saved to {midi_path}")

    print(
        Fore.GREEN
        + "\n✅ Partimento generation, realization, review, and export completed successfully!"
    )

    # Write metadata.json summarizing the chain
    meta_path = os.path.join(chain_dir, "metadata.json")
    files_dict = {
        "partimento_versions": partimento_versions,
        "review_partimento_versions": review_partimento_versions,
        "realized": os.path.basename(realized_path),
        "musicxml": os.path.basename(xml_path),
        "midi": os.path.basename(midi_path),
    }
    if realization_versions:
        files_dict["realization_versions"] = [
            os.path.basename(realized_path)
        ] + realization_versions
        # Add reviews
        files_dict["review_realization_versions"] = [
            f"review_realization_{i+1}.json" for i in range(len(realization_versions))
        ]
    else:
        files_dict["review_realization"] = "review_realization_1.json"

    with open(meta_path, "w") as f:
        json.dump(
            {
                "id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat() + "Z",
                "mode": "chain-partimento",
                "prompt": args.prompt,
                "files": files_dict,
                "patched": {
                    "partimento": bool(partimento_patch),
                    "realized": bool(realization_patch),
                },
                "version": "0.1.0",
            },
            f,
            indent=2,
        )
    print(Fore.GREEN + f"\n📦 Metadata saved to {meta_path}")

    print(Fore.CYAN + f"\n🎧 Writing OGG file: {midi_path}")
    if not os.path.exists(midi_path):
        print(Fore.RED + "❌ MIDI file not found.")
        return

    print(Fore.GREEN + "\n📊 Summary:")
    print(Fore.YELLOW + f"📄 Chain ID: {os.path.basename(chain_dir)}")
    print(Fore.YELLOW + f"📁 Output dir: {chain_dir}")
    print(Fore.YELLOW + f"🎼 Prompt style: {args.prompt}")
    print(Fore.YELLOW + f"🎧 Audio preview: {ogg_path}")
    print(Fore.YELLOW + f"📝 Iterations: {args.iterations}")
    print(Fore.CYAN + f"\n🔗 Complete. Data is stored in {chain_dir}")
    print(Fore.YELLOW + f"🎶 Ready for realization: {os.path.basename(json_path)}")

    # Try Timidity first
    try:
        subprocess.run(["timidity", midi_path], check=True)
        open_file_if_possible(ogg_path)
        return
    except FileNotFoundError:
        print(
            Fore.YELLOW
            + "⚠️  Timidity not found. Falling back to system default player..."
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

    # Determine output path: prefer chain-style if output is a directory
    if args.output and os.path.isdir(args.output):
        chain_dir = args.output
        os.makedirs(chain_dir, exist_ok=True)
        # Use timestamp for consistency
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = os.path.join(chain_dir, "review_realization.json")
    else:
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

    # Write metadata.json if using a chain directory
    if args.output and os.path.isdir(args.output):
        meta_path = os.path.join(args.output, "metadata.json")
        import uuid

        meta = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat() + "Z",
            "mode": "review-score",
            "source_file": args.input,
            "review_file": os.path.basename(output_path),
            "version": "0.1.0",
        }
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)


def handle_review_partimento(args):
    print(Fore.CYAN + f"\n🔍 Reviewing partimento from {args.input}...")
    review_json = review_partimento(args.input, call_llm)
    review_data = json.loads(review_json)

    from utils.metadata_utils import generate_metadata

    metadata = generate_metadata(args.input, "review-partimento")
    output = {**metadata, "data": review_data}

    # Determine output path: prefer chain-style if output is a directory
    if args.output and os.path.isdir(args.output):
        chain_dir = args.output
        os.makedirs(chain_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = os.path.join(chain_dir, "review_partimento.json")
    else:
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

    # Write metadata.json if using a chain directory
    if args.output and os.path.isdir(args.output):
        meta_path = os.path.join(args.output, "metadata.json")
        import uuid

        meta = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat() + "Z",
            "mode": "review-partimento",
            "source_file": args.input,
            "review_file": os.path.basename(output_path),
            "version": "0.1.0",
        }
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)


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

    # Determine output path: prefer chain-style if output is a directory
    if args.output and os.path.isdir(args.output):
        chain_dir = args.output
        os.makedirs(chain_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = os.path.join(chain_dir, "revised.json")
    else:
        os.makedirs("generated/json", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = (
            args.output or f"generated/json/revised_partimento_{timestamp}.json"
        )

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


def handle_write_audio(args):
    import os
    import shutil

    from colorama import Fore

    # If args.output is a directory, copy input file there for playback
    midi_path = args.input
    output_playback_path = None
    if hasattr(args, "output") and args.output and os.path.isdir(args.output):
        # Place the MIDI file in the shared output directory under a canonical name
        output_playback_path = os.path.join(args.output, os.path.basename(args.input))
        if os.path.abspath(midi_path) != os.path.abspath(output_playback_path):
            shutil.copy2(midi_path, output_playback_path)
        midi_path = output_playback_path

    print(Fore.CYAN + f"\n🎧 Writing OGG file: {midi_path}")
    if not os.path.exists(midi_path):
        print(Fore.RED + "❌ MIDI file not found.")
        return

    # Try Timidity first
    try:
        subprocess.run(["timidity", midi_path], check=True)
        return
    except FileNotFoundError:
        print(
            Fore.YELLOW
            + "⚠️  Timidity not found. Falling back to system default player..."
        )

    # Fallback: system-specific
    if sys.platform.startswith("darwin"):
        subprocess.run(["open", midi_path])
    elif sys.platform.startswith("win"):
        os.startfile(midi_path)
    elif sys.platform.startswith("linux"):
        subprocess.run(["xdg-open", midi_path])
    else:
        print(Fore.RED + "❌ Unsupported OS for playback.")


# === HANDLER MAP ===
# Dispatch map for all CLI commands to their corresponding handler functions.

handler_map = {
    "describe-chain": handle_describe_chain,
    "chain-partimento": handle_chain_partimento_realization,
    "chain-partimento-only": handle_chain_partimento_only,
    "lead-sheet": handle_lead_sheet,
    "generate-partimento": handle_partimento,
    "export-partimento-to-musicxml": handle_export_partimento_to_musicxml,
    "export-realized-partimento-to-musicxml": handle_export_realized_partimento_to_musicxml,
    "realize-partimento": handle_realize_partimento,
    "inspect-musicxml": handle_inspect_musicxml,
    "review-score": handle_review_score,
    "review-partimento": handle_review_partimento,
    "revise-score": handle_revise_score,
    "export-audio": handle_write_audio,
}
