import json
import os
import re
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

from colorama import Fore, Style

from genres.partimento.tasks import generate as genarate_partimento
from genres.partimento.tasks import realize
from genres.partimento.tasks.export import (
    export_partimento_to_midi,
    export_partimento_to_musicxml,
    export_realized_partimento_to_midi,
    export_realized_partimento_to_musicxml,
)
from genres.partimento.tasks.realize import realize_partimento_satb
from genres.partimento.tasks.review import review_partimento, review_realized_score
from lib.analysis.linting import lint_satb
from lib.utils.json_utils import apply_patch
from lib.utils.llm_utils import call_llm
from lib.utils.metadata_utils import generate_metadata
from lib.utils.playback_utils import open_file_if_possible


def handle_chain_partimento_only(args):
    print(Fore.CYAN + f"\n🎼 Generating and reviewing partimento...")

    # Create a unified output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    chain_dir = args.output or f"generated/chains/partimento_{timestamp}"
    os.makedirs(chain_dir, exist_ok=True)

    base_json_path = os.path.join(chain_dir, "partimento_01.json")
    xml_path = os.path.join(chain_dir, "partimento.musicxml")

    # Step 1: Generate partimento
    partimento_data = genarate_partimento.generate_partimento(args.prompt, call_llm)
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

        iter_review_path = os.path.join(chain_dir, f"review_partimento_{i+1:02}.json")
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

        # Write updated file with zero-padded numeric suffix
        new_json_path = os.path.join(chain_dir, f"partimento_{i+2:02}.json")
        working_data["data"] = updated
        with open(new_json_path, "w") as f:
            json.dump(working_data, f, indent=2)
        print(Fore.YELLOW + f"\n✅ Patch applied and saved to {new_json_path}")
        current_json_path = new_json_path
        partimento_versions.append(os.path.basename(new_json_path))

    # Step 3: Export to MusicXML (use last version)
    print(Fore.CYAN + f"\n🎼 Exporting final partimento to MusicXML...")
    export_partimento(current_json_path, xml_path)
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
        "midi": os.path.basename(midi_path),
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
    ogg_path = midi_path.replace(".mid", ".ogg")
    print(Fore.YELLOW + f"🎧 Audio preview: {ogg_path}")
    print(Fore.YELLOW + f"📝 Iterations: {args.iterations}")
    print(Fore.CYAN + f"\n🔗 Complete. Data is stored in {chain_dir}")

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


def handle_generate_partimento(args):
    print(Fore.CYAN + f"\n🎼 Generating partimento bass line from prompt...")
    partimento_data = genarate_partimento.generate_partimento(args.prompt, call_llm)
    output = {
        **generate_metadata(args.prompt, "generate-partimento"),
        "data": partimento_data,
    }
    output_json = json.dumps(output, indent=2)
    print(Fore.GREEN + "\n✅ Generated partimento:\n" + Style.RESET_ALL + output_json)

    # Helper function to check if a path is likely a directory (no file extension)
    def is_likely_directory(path):
        return not os.path.splitext(path)[1]

    # Determine output path using chain-aware logic
    if args.output and is_likely_directory(args.output):
        chain_dir = args.output
        os.makedirs(chain_dir, exist_ok=True)
        json_path = os.path.join(chain_dir, "partimento.json")
        xml_path = os.path.join(chain_dir, "partimento.musicxml")
        is_chain = True
    else:
        os.makedirs("generated/json", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        json_path = args.output or f"generated/json/partimento_{timestamp}.json"
        xml_path = json_path.replace(".json", ".musicxml")
        is_chain = False

    with open(json_path, "w") as f:
        f.write(output_json)
    print(Fore.YELLOW + f"\n💾 Saved to {json_path}")

    # Export to MusicXML
    export_partimento_to_musicxml(json_path, xml_path)
    export_partimento_to_midi(json_path, xml_path.replace(".musicxml", ".mid"))

    # Write metadata.json if using a chain directory
    if is_chain:
        meta_path = os.path.join(chain_dir, "metadata.json")
        metadata = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat() + "Z",
            "mode": "generate-partimento",
            "prompt": args.prompt,
            "files": {
                "partimento": os.path.basename(json_path),
                "musicxml": os.path.basename(xml_path),
            },
            "version": "0.1.0",
        }
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)


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
    partimento_data = genarate_partimento.generate_partimento(args.prompt, call_llm)
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

    # --- LINT SATB ---------------------------------------------------------
    lint_report = lint_satb(realization)
    print(Fore.CYAN + "\n🧹 Voice‑leading linter result:")
    if lint_report["issues"]:
        print(Fore.RED + f"❌ {len(lint_report['issues'])} issues found:")
        for issue in lint_report["issues"]:
            print(Fore.RED + f"  - {issue}")
    else:
        print(Fore.GREEN + "✅ No voice‑leading issues detected.")

    # Skip LLM review if linter found no issues and user didn't force iterations > 0
    if not lint_report["issues"]:
        print(Fore.GREEN + "🔍 Linter clean; skipping LLM realization review passes.")
        realization_versions = []
    else:
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
            print(
                Fore.GREEN + review_data.get("message", "No review message provided.")
            )

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
                        **generate_metadata(
                            args.prompt, f"realize-partimento-pass-{i+1}"
                        ),
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
                    print(
                        Fore.YELLOW
                        + "⚠️  Timidity not found. Skipping OGG audio export."
                    )

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
    realized_data = realize.realize_partimento_satb(args.input, call_llm)
    print(
        Fore.GREEN
        + "\n✅ Realized partimento:\n"
        + Style.RESET_ALL
        + json.dumps(realized_data, indent=2)
    )

    # Helper function to check if a path is likely a directory (no file extension)
    def is_likely_directory(path):
        return not os.path.splitext(path)[1]

    # Helper to write realization JSON with metadata
    def write_realization_json(
        data, output_path, *, mode, source_path=None, prompt=None
    ):
        payload = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat() + "Z",
            "mode": mode,
            "source": source_path or "unknown",
            "user_prompt": prompt or None,
            "version": "0.1.0",
            "data": data,
        }
        with open(output_path, "w") as f:
            json.dump(payload, f, indent=2)

    def write_partimento_json(
        data, output_path, *, mode, source_path=None, prompt=None
    ):
        payload = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat() + "Z",
            "mode": mode,
            "source": source_path or "unknown",
            "user_prompt": prompt or None,
            "version": "0.1.0",
            "data": data,
        }
        with open(output_path, "w") as f:
            json.dump(payload, f, indent=2)

    # Determine output path and whether it's a "chain" directory
    if args.output and is_likely_directory(args.output):
        os.makedirs(args.output, exist_ok=True)
        output_path = os.path.join(args.output, "realized.json")
        is_chain = True
    else:
        os.makedirs("generated/json", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = (
            args.output or f"generated/json/realized_partimento_{timestamp}.json"
        )
        is_chain = False

    # Load partimento.json as full metadata-wrapped source and extract values
    if os.path.exists(args.input):
        with open(args.input, "r") as f:
            source_data = json.load(f)
        source = args.input
        prompt = source_data.get("user_prompt") or source_data.get("prompt")
    else:
        source = args.input
        prompt = None

    write_realization_json(
        realized_data,
        output_path,
        mode="realize-partimento",
        source_path=source,
        prompt=prompt,
    )
    print(Fore.YELLOW + f"\n💾 Saved to {output_path}")

    # Write metadata.json and copy original partimento if using a chain directory
    if is_chain:
        # Also copy the input partimento into the chain folder if not already there
        partimento_copy_path = os.path.join(args.output, "partimento.json")
        if not os.path.exists(partimento_copy_path):
            with open(args.input, "r") as f:
                part_data = json.load(f)
                write_partimento_json(
                    part_data,
                    partimento_copy_path,
                    mode="partimento",
                    source_path=source,
                    prompt=prompt,
                )

        meta_path = os.path.join(args.output, "metadata.json")
        meta = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat() + "Z",
            "mode": "realize-partimento",
            "source_file": args.input,
            "realized_file": os.path.basename(output_path),
            "partimento_file": os.path.basename(partimento_copy_path),
            "version": "0.1.0",
        }
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)


def handle_export_partimento(args):
    print(Fore.CYAN + f"\n🎼 Exporting partimento JSON from {args.input}...")

    if args.output and not Path(args.output).suffix:
        os.makedirs(args.output, exist_ok=True)
        musicxml_path = os.path.join(args.output, "partimento.musicxml")
        midi_path = os.path.join(args.output, "partimento.mid")
    else:
        base = args.output or args.input
        stem = Path(base).with_suffix("").as_posix()
        musicxml_path = f"{stem}.musicxml"
        midi_path = f"{stem}.mid"

    print(Fore.CYAN + f"  ➤ Exporting MusicXML to {musicxml_path} ...")
    export_partimento_to_musicxml(args.input, musicxml_path)
    print(Fore.YELLOW + f"🎼 MusicXML saved to {musicxml_path}")
    print(Fore.CYAN + f"  ➤ Exporting MIDI to {midi_path} ...")
    export_partimento_to_midi(args.input, midi_path)
    print(Fore.YELLOW + f"🎧 MIDI saved to {midi_path}")

    # Export OGG audio
    ogg_path = midi_path.replace(".mid", ".ogg")
    print(Fore.CYAN + f"  ➤ Converting MIDI to OGG: {ogg_path}")
    if os.path.exists(midi_path):
        try:
            subprocess.run(["timidity", midi_path, "-Ow", "-o", ogg_path], check=True)
            print(Fore.YELLOW + f"🎧 OGG audio saved to {ogg_path}")
        except FileNotFoundError:
            print(Fore.YELLOW + "⚠️  Timidity not found. Skipping OGG audio export.")
    else:
        print(Fore.RED + "❌ MIDI file not found. Cannot convert to OGG.")


def handle_export_realization(args):
    print(Fore.CYAN + f"\n🎼 Exporting realized partimento JSON from {args.input}...")

    if args.output and not Path(args.output).suffix:
        os.makedirs(args.output, exist_ok=True)
        musicxml_path = os.path.join(args.output, "realized.musicxml")
        midi_path = os.path.join(args.output, "realized.mid")
    else:
        base = args.output or args.input
        stem = Path(base).with_suffix("").as_posix()
        musicxml_path = f"{stem}.musicxml"
        midi_path = f"{stem}.mid"

    print(Fore.CYAN + f"  ➤ Exporting MusicXML to {musicxml_path} ...")
    export_realized_partimento_to_musicxml(args.input, musicxml_path)
    print(Fore.YELLOW + f"🎼 MusicXML saved to {musicxml_path}")
    print(Fore.CYAN + f"  ➤ Exporting MIDI to {midi_path} ...")
    export_realized_partimento_to_midi(args.input, midi_path)
    print(Fore.YELLOW + f"🎧 MIDI saved to {midi_path}")
    # Export OGG audio
    ogg_path = midi_path.replace(".mid", ".ogg")
    print(Fore.CYAN + f"  ➤ Converting MIDI to OGG: {ogg_path}")
    if os.path.exists(midi_path):
        try:
            subprocess.run(["timidity", midi_path, "-Ow", "-o", ogg_path], check=True)
            print(Fore.YELLOW + f"🎧 OGG audio saved to {ogg_path}")
        except FileNotFoundError:
            print(Fore.YELLOW + "⚠️  Timidity not found. Skipping OGG audio export.")
    else:
        print(Fore.RED + "❌ MIDI file not found. Cannot convert to OGG.")


# === REVIEW AND REVISE ===
# Includes functions to review partimenti and SATB realizations, and to apply patches.


def write_review_json(data, output_path, *, mode, source_path=None, prompt=None):
    payload = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat() + "Z",
        "mode": mode,
        "source": source_path or "unknown",
        "user_prompt": prompt or None,
        "version": "0.1.0",
        "data": data,
    }
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2)


def handle_review_realization(args):
    print(Fore.CYAN + f"\n🔍 Reviewing realized partimento from {args.input}...")
    review_json = review_realized_score(args.input, call_llm)
    review_data = json.loads(review_json)

    # Determine output path: prefer chain-style if output is a directory
    if args.output and os.path.isdir(args.output):
        chain_dir = args.output
        os.makedirs(chain_dir, exist_ok=True)
        output_path = os.path.join(chain_dir, "review_realization.json")
    else:
        os.makedirs("generated/review", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = f"generated/review/review_{timestamp}.json"

    write_review_json(
        review_data, output_path, mode="review-score", source_path=args.input
    )

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
    import re
    from pathlib import Path

    print(Fore.CYAN + f"\n🔍 Reviewing partimento from {args.input}...")
    review_json = review_partimento(args.input, call_llm)
    review_data = json.loads(review_json)

    # Helper function to check if a path is likely a directory (no file extension)
    def is_likely_directory(path):
        return not os.path.splitext(path)[1]

    # Determine output path: prefer chain-style if output is a directory or likely directory, and increment filename
    if args.output and is_likely_directory(args.output):
        chain_dir = args.output
        os.makedirs(chain_dir, exist_ok=True)
        base_name = "review_partimento"
        existing_files = list(Path(chain_dir).glob(f"{base_name}_*.json"))
        existing_numbers = [
            int(re.search(r"_(\d+)\.json", str(f)).group(1))
            for f in existing_files
            if re.search(r"_(\d+)\.json", str(f))
        ]
        next_num = max(existing_numbers, default=0) + 1
        output_path = os.path.join(chain_dir, f"{base_name}_{next_num}.json")
    else:
        os.makedirs("generated/review", exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = f"generated/review/review_{timestamp}.json"

    write_review_json(
        review_data, output_path, mode="review-partimento", source_path=args.input
    )

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
    if args.output and is_likely_directory(args.output):
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


def handle_revise_realization(args):
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

    # Determine output path: prefer chain-style if output is a directory
    if args.output and os.path.isdir(args.output):
        chain_dir = args.output
        os.makedirs(chain_dir, exist_ok=True)
        input_stem = Path(args.input).stem.replace(".json", "").replace("_", "-")
        existing_files = list(Path(chain_dir).glob(f"{input_stem}_*.json"))
        revision_numbers = [
            int(re.search(r"_(\d+)\.json", str(f)).group(1))
            for f in existing_files
            if re.search(r"_(\d+)\.json", str(f))
        ]
        next_rev = max(revision_numbers, default=0) + 1
        output_path = os.path.join(chain_dir, f"{input_stem}_{next_rev}.json")
    else:
        os.makedirs("generated/json", exist_ok=True)
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = (
            args.output or f"generated/json/revised_partimento_{timestamp}.json"
        )

    write_review_json(
        updated_data, output_path, mode="revise-partimento", source_path=args.input
    )

    print(Fore.YELLOW + f"\n✅ Revised realization saved to {output_path}")


def handler_revise_partimento(args):
    print(Fore.CYAN + f"\n🔧 Revising partimento based on patch...")

    with open(args.input, "r") as f:
        original = json.load(f)

    with open(args.patch, "r") as f:
        review = json.load(f)

    patch = review.get("data", {}).get("suggested_patch")
    if not patch:
        print(Fore.RED + "❌ No suggested_patch found in review file.")
        return

    updated_data = apply_patch(original["data"], patch)

    # Determine output path: prefer chain-style if output is a directory
    if args.output and os.path.isdir(args.output):
        chain_dir = args.output
        os.makedirs(chain_dir, exist_ok=True)
        input_stem = Path(args.input).stem.replace(".json", "").replace("_", "-")
        existing_files = list(Path(chain_dir).glob(f"{input_stem}_*.json"))
        revision_numbers = [
            int(re.search(r"_(\d+)\.json", str(f)).group(1))
            for f in existing_files
            if re.search(r"_(\d+)\.json", str(f))
        ]
        next_rev = max(revision_numbers, default=0) + 1
        output_path = os.path.join(chain_dir, f"{input_stem}_{next_rev}.json")
    else:
        os.makedirs("generated/json", exist_ok=True)
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = (
            args.output or f"generated/json/revised_partimento_{timestamp}.json"
        )

    write_review_json(
        updated_data, output_path, mode="revise-partimento", source_path=args.input
    )

    print(Fore.YELLOW + f"\n✅ Revised partimento saved to {output_path}")


handler_map = {
    # full chains
    "chain-partimento-realization": handle_chain_partimento_realization,
    "chain-partimento-only": handle_chain_partimento_only,
    # generate
    "generate-partimento": handle_generate_partimento,
    "realize-partimento": handle_realize_partimento,
    # review
    "review-partimento": handle_review_partimento,
    "review-realization": handle_review_realization,
    # revise
    "revise-realization": handle_revise_realization,
    "revise-partimento": handler_revise_partimento,
    # export
    "export-partimento": handle_export_partimento,
    "export-realization": handle_export_realization,
}
