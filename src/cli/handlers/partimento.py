import json
import logging
import subprocess
import uuid
from argparse import Namespace
from datetime import datetime
from pathlib import Path

from colorama import Fore, Style
from rich.logging import RichHandler

from genres.partimento.tasks import generate as generate_partimento
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
from lib.utils.chain_utils import (
    build_meta,
    get_next_versioned_filename,
    is_likely_directory,
    log_step,
    pretty_summary,
    resolve_output,
    write_chain_json,
    write_metadata,
)
from lib.utils.json_utils import apply_patch
from lib.utils.llm_utils import call_llm
from lib.utils.music_utils import export_ogg_from_midi
from lib.utils.playback_utils import open_file_if_possible

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger(__name__)


# ============== Partimento Handlers ==============


def handle_chain_partimento_only(args: Namespace) -> None:
    """Run the classic partimento chain: generate, review (with optional patching), export (MusicXML, MIDI, OGG), and save all results to a chain directory."""
    log_step(f"\n🎼 Generating and reviewing partimento...")

    # Create a unified output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    chain_dir = (
        Path(args.output)
        if args.output
        else Path(f"generated/chains/partimento_{timestamp}")
    )
    chain_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Generate partimento
    partimento_data = generate_partimento.generate_partimento(args.prompt, call_llm)
    base_json_path = chain_dir / "partimento_01.json"
    write_chain_json(
        partimento_data,
        base_json_path,
        mode="generate-partimento",
        source_path=None,
        prompt=args.prompt,
    )
    log_step(f"\n💾 Partimento saved to {base_json_path}", color=Fore.YELLOW)

    # Step 2: Review partimento with iteration support, storing each version
    iterations = getattr(args, "iterations", 1)
    current_json_path = base_json_path
    partimento_versions = [Path(base_json_path).name]
    review_versions = []
    for i in range(iterations):
        log_step(f"\n🔍 Reviewing partimento (pass {i+1})...")
        review_json = review_partimento(current_json_path, call_llm)
        review_data = json.loads(review_json)

        # Use helper for review file name
        review_json_path = get_next_versioned_filename(
            str(chain_dir), "review_partimento"
        )
        write_chain_json(
            review_data,
            review_json_path,
            mode=f"review-partimento-pass-{i+1}",
            source_path=current_json_path,
            prompt=args.prompt,
        )
        log_step(f"\n✅ Review saved to {review_json_path}", color=Fore.GREEN)
        log_step("\n💬 Review Summary:", color=Fore.YELLOW)
        logger.info(
            Fore.GREEN
            + review_data.get("message", "No review message provided.")
            + Style.RESET_ALL
        )
        review_versions.append(Path(review_json_path).name)

        patch = review_data.get("suggested_patch")
        if not patch:
            log_step("No patch suggested. Stopping review loop.", color=Fore.YELLOW)
            break

        # Load current version and apply patch
        with open(current_json_path, "r") as f:
            working_data = json.load(f)
        updated = apply_patch(working_data["data"], patch)

        # Write updated file with versioned filename
        new_json_path = get_next_versioned_filename(str(chain_dir), "partimento")
        working_data["data"] = updated
        write_chain_json(
            working_data["data"],
            new_json_path,
            mode="patched-partimento",
            source_path=current_json_path,
            prompt=args.prompt,
        )
        log_step(f"\n✅ Patch applied and saved to {new_json_path}", color=Fore.YELLOW)
        current_json_path = new_json_path
        partimento_versions.append(Path(new_json_path).name)

    # Step 3: Export to MusicXML (use last version)
    log_step(f"\n🎼 Exporting final partimento to MusicXML...")
    xml_path = chain_dir / "partimento.musicxml"
    export_partimento_to_musicxml(current_json_path, str(xml_path))
    log_step(f"\n✅ MusicXML saved to {xml_path}", color=Fore.YELLOW)
    # Export to MIDI
    midi_path = chain_dir / "partimento.mid"
    export_partimento_to_midi(current_json_path, str(midi_path))
    log_step(f"🎧 MIDI saved to {midi_path}", color=Fore.YELLOW)

    # Write metadata
    files_dict = {
        "partimento_versions": partimento_versions,
        "review_versions": review_versions,
        "musicxml": Path(xml_path).name,
        "midi": Path(midi_path).name,
    }
    write_metadata(
        chain_dir,
        {
            "id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "mode": "generate-and-review-partimento",
            "prompt": args.prompt,
            "files": files_dict,
            "version": "0.1.0",
        },
    )
    log_step(f"\n📦 Metadata saved to {chain_dir / 'metadata.json'}", color=Fore.GREEN)

    ogg_path = midi_path.with_suffix(".ogg")

    logger.info("\n📊 Summary:")
    logger.info(f"📄 Chain ID: {chain_dir.name}")
    logger.info(f"📁 Output dir: {chain_dir}")
    logger.info(f"🎼 Prompt style: {args.prompt}")
    logger.info(f"🎧 Audio preview: {ogg_path}")
    logger.info(f"📝 Iterations: {args.iterations}")
    logger.info(f"\n🔗 Complete. Data is stored in {chain_dir}")

    log_step(f"\n🎧 Writing OGG file: {ogg_path}")
    export_ogg_from_midi(str(midi_path), str(ogg_path))


def handle_chain_partimento_realization(args: Namespace) -> None:
    """Run the full realization chain: generate partimento, review/patch, realize SATB, review/patch realization, export, and write all artifacts to a chain directory."""
    log_step(
        "\n🔗 Generating → Reviewing → Realizing → Reviewing → Exporting partimento..."
    )

    # Step 1: Setup output directory
    log_step("\n🔗 1. Generating Partimento...")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    chain_dir = (
        Path(args.output)
        if args.output
        else Path(f"generated/chains/partimento_{timestamp}")
    )
    chain_dir.mkdir(parents=True, exist_ok=True)

    # Step 2: Generate partimento (use versioned filename)
    partimento_json_path = get_next_versioned_filename(str(chain_dir), "partimento")
    partimento_data = generate_partimento.generate_partimento(args.prompt, call_llm)
    write_chain_json(
        partimento_data,
        partimento_json_path,
        mode="generate-partimento",
        source_path=None,
        prompt=args.prompt,
    )
    log_step(f"\n💾 Partimento saved to {partimento_json_path}", color=Fore.YELLOW)

    # Step 3: Review partimento (with patching and versioning)
    partimento_versions = [Path(partimento_json_path).name]
    review_partimento_versions = []
    current_partimento_path = partimento_json_path
    current_partimento_data = partimento_data
    partimento_patch = None
    for i in range(args.iterations):
        log_step(f"\n🔍 Reviewing partimento (pass {i+1})...")
        review_json = review_partimento(current_partimento_path, call_llm)
        review_data = json.loads(review_json)
        review_json_path = get_next_versioned_filename(
            str(chain_dir), "review_partimento"
        )
        write_chain_json(
            review_data,
            review_json_path,
            mode=f"review-partimento-pass-{i+1}",
            source_path=current_partimento_path,
            prompt=args.prompt,
        )
        log_step(f"\n✅ Review saved to {review_json_path}", color=Fore.GREEN)
        log_step("\n💬 Partimento Review:", color=Fore.YELLOW)
        logger.info(
            Fore.GREEN
            + review_data.get("message", "No review message provided.")
            + Style.RESET_ALL
        )
        review_partimento_versions.append(Path(review_json_path).name)

        partimento_patch = review_data.get("suggested_patch")
        if not partimento_patch:
            log_step("No patch suggested. Stopping review loop.", color=Fore.YELLOW)
            break

        # Load and apply patch
        with open(current_partimento_path, "r") as f:
            current_data = json.load(f)
        patched = apply_patch(current_data["data"], partimento_patch)

        # Write patched version (use versioned filename)
        patched_json_path = get_next_versioned_filename(str(chain_dir), "partimento")
        write_chain_json(
            patched,
            patched_json_path,
            mode="patched-partimento",
            source_path=current_partimento_path,
            prompt=args.prompt,
        )
        log_step(
            f"\n✅ Patch applied. Updated partimento saved to {patched_json_path}",
            color=Fore.YELLOW,
        )
        current_partimento_path = patched_json_path
        partimento_versions.append(Path(patched_json_path).name)
        current_partimento_data = patched

    # After review loop, set json_path and partimento_data to last version
    json_path = current_partimento_path
    partimento_data = current_partimento_data

    # Export partimento to MIDI (for OGG export)
    midi_path = chain_dir / "partimento.mid"
    log_step(f"\n🎼 Exporting partimento MIDI to {midi_path} ...")
    export_partimento_to_midi(current_partimento_path, str(midi_path))
    log_step(f"🎧 Partimento MIDI saved to {midi_path}", color=Fore.YELLOW)

    # Export OGG for partimento
    ogg_path = midi_path.with_suffix(".ogg")
    log_step(f"🎧 Exporting OGG audio for partimento: {ogg_path}")
    export_ogg_from_midi(str(midi_path), str(ogg_path))

    # Step 4: Realize partimento (SATB)
    log_step(f"\n🔗 3. Realizing partimento...")
    realization = realize_partimento_satb(partimento_data, call_llm)
    realized_path = get_next_versioned_filename(chain_dir, "realized")
    write_chain_json(
        realization,
        realized_path,
        mode="realize-partimento",
        source_path=current_partimento_path,
        prompt=args.prompt,
    )
    log_step(f"\n🎶 Realization saved to {realized_path}", color=Fore.YELLOW)

    # --- LINT SATB ---------------------------------------------------------
    lint_report = lint_satb(realization)
    log_step("\n🧹 Voice‑leading linter result:")
    if lint_report["issues"]:
        logger.warning(
            Fore.RED
            + f"❌ {len(lint_report['issues'])} issues found:"
            + Style.RESET_ALL
        )
        for issue in lint_report["issues"]:
            logger.warning(Fore.RED + f"  - {issue}" + Style.RESET_ALL)
    else:
        logger.info(
            Fore.GREEN + "✅ No voice-leading issues detected." + Style.RESET_ALL
        )

    # Step 5: Review realization if linter found issues, else skip
    if not lint_report["issues"]:
        log_step(
            "🔍 Linter clean; skipping LLM realization review passes.", color=Fore.GREEN
        )
        realization_versions = []
        review_realization_versions = []
        last_realized_path = realized_path
        realization_patch = None
    else:
        # === Multiple review loops for realization ===
        realization_versions = []
        review_realization_versions = []
        last_realized_path = realized_path
        realization_patch = None
        for i in range(args.iterations):
            input_path = last_realized_path
            review_json_path = get_next_versioned_filename(
                str(chain_dir), "review_realization"
            )
            realized_version_path = get_next_versioned_filename(
                str(chain_dir), "realized"
            )

            # Review
            log_step(f"\n🔍 Reviewing realization (pass {i+1})...")
            review_json = review_realized_score(input_path, call_llm)
            review_data = json.loads(review_json)
            write_chain_json(
                review_data,
                review_json_path,
                mode=f"review-realization-pass-{i+1}",
                source_path=input_path,
                prompt=args.prompt,
            )
            log_step(
                f"\n🔍 Review {i+1} completed and saved to {review_json_path}.",
                color=Fore.YELLOW,
            )
            logger.info(
                Fore.GREEN
                + review_data.get("message", "No review message provided.")
                + Style.RESET_ALL
            )
            review_realization_versions.append(Path(review_json_path).name)

            realization_patch = review_data.get("suggested_patch")
            if not realization_patch:
                log_step("No patch suggested; stopping review loop.", color=Fore.YELLOW)
                break

            # Patch realization
            with open(input_path, "r") as f:
                current_data = json.load(f)["data"]
            updated = apply_patch(current_data, realization_patch)
            write_chain_json(
                updated,
                realized_version_path,
                mode=f"realize-partimento-pass-{i+1}",
                source_path=input_path,
                prompt=args.prompt,
            )
            log_step(
                f"✅ Patch applied: {Path(realized_version_path).name}",
                color=Fore.YELLOW,
            )
            realization_versions.append(Path(realized_version_path).name)
            last_realized_path = realized_version_path

            # Export MIDI and OGG for this realization version
            midi_version_path = Path(realized_version_path).with_suffix(".mid")
            export_realized_partimento_to_midi(
                realized_version_path, str(midi_version_path)
            )
            ogg_version_path = Path(realized_version_path).with_suffix(".ogg")
            log_step(f"🎧 Exporting OGG audio for realization: {ogg_version_path}")
            export_ogg_from_midi(str(midi_version_path), str(ogg_version_path))

    # Step 6: Export final realization to MusicXML and MIDI/OGG
    final_realized = last_realized_path
    xml_path = chain_dir / "realized.musicxml"
    midi_path = chain_dir / "realized.mid"
    log_step(f"\n🔗 5. Exporting realization to MusicXML and MIDI...")
    export_realized_partimento_to_musicxml(final_realized, str(xml_path))
    log_step(f"🎼 MusicXML saved to {xml_path}", color=Fore.YELLOW)
    export_realized_partimento_to_midi(final_realized, str(midi_path))
    log_step(f"🎧 MIDI saved to {midi_path}", color=Fore.YELLOW)
    ogg_path = midi_path.with_suffix(".ogg")
    log_step(f"🎧 Exporting OGG audio for realization: {ogg_path}")
    export_ogg_from_midi(str(midi_path), str(ogg_path))

    log_step(
        "\n✅ Partimento generation, realization, review, and export completed successfully!",
        color=Fore.GREEN,
    )

    # Step 7: Write metadata.json summarizing the chain
    files_dict = {
        "partimento_versions": partimento_versions,
        "review_partimento_versions": review_partimento_versions,
        "realized": Path(realized_path).name,
        "musicxml": Path(xml_path).name,
        "midi": Path(midi_path).name,
    }
    if realization_versions:
        files_dict["realization_versions"] = [
            Path(realized_path).name
        ] + realization_versions
        files_dict["review_realization_versions"] = review_realization_versions
    else:
        files_dict["review_realization"] = (
            review_realization_versions[0] if review_realization_versions else None
        )

    write_metadata(
        chain_dir,
        {
            "id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "mode": "chain-partimento",
            "prompt": args.prompt,
            "files": files_dict,
            "patched": {
                "partimento": bool(partimento_patch),
                "realized": (
                    bool(realization_patch)
                    if "realization_patch" in locals()
                    else False
                ),
            },
            "version": "0.1.0",
        },
    )
    log_step(f"\n📦 Metadata saved to {chain_dir / 'metadata.json'}", color=Fore.GREEN)

    # Final summary
    log_step(f"\n🎧 Writing OGG file: {midi_path.with_suffix('.ogg')}")
    if not midi_path.exists():
        logger.error(Fore.RED + "❌  MIDI file not found." + Style.RESET_ALL)
        return

    logger.info("\n📊 Summary:")
    logger.info(f"📄 Chain ID: {chain_dir.name}")
    logger.info(f"📁 Output dir: {chain_dir}")
    logger.info(f"🎼 Prompt style: {args.prompt}")
    logger.info(f"🎧 Audio preview: {ogg_path}")
    logger.info(f"📝 Iterations: {args.iterations}")
    logger.info(f"\n🔗 Complete. Data is stored in {chain_dir}")
    logger.info(f"🎶 Ready for realization: {Path(json_path).name}")

    # Try Timidity for playback
    try:
        subprocess.run(["timidity", str(midi_path)], check=True)
        open_file_if_possible(ogg_path)
        return
    except FileNotFoundError:
        logger.warning(
            Fore.YELLOW
            + "⚠️  Timidity not found. Falling back to system default player..."
            + Style.RESET_ALL
        )


def handle_generate_partimento(args: Namespace) -> None:
    """Generate a partimento from a prompt, save to chain or flat file, and export MusicXML/MIDI."""
    log_step("\n🎼 Generating partimento bass line from prompt...")
    partimento_data = generate_partimento.generate_partimento(args.prompt, call_llm)

    out = resolve_output("partimento", args)

    # -- write JSON --------------------------------------------------------
    write_chain_json(
        partimento_data,
        out.json,
        mode="generate-partimento",
        source_path=None,
        prompt=args.prompt,
    )
    log_step(f"\n💾 JSON saved to {out.json}", color=Fore.YELLOW)

    # -- exports -----------------------------------------------------------
    export_partimento_to_musicxml(out.json, out.xml)
    export_partimento_to_midi(out.json, out.midi)
    export_ogg_from_midi(out.midi, out.ogg)

    # -- metadata ----------------------------------------------------------
    if out.is_chain:
        write_metadata(
            out.chain_dir,
            build_meta(
                "generate-partimento",
                args.prompt,
                {
                    "partimento": out.json.name,
                    "musicxml": out.xml.name,
                    "midi": out.midi.name,
                    "ogg": out.ogg.name,
                },
            ),
        )
        log_step(
            f"\n📦 Metadata written to {out.chain_dir / 'metadata.json'}",
            color=Fore.GREEN,
        )

    # -- summary -----------------------------------------------------------
    pretty_summary(out, iterations=getattr(args, "iterations", 1))


def handle_realize_partimento(args: Namespace) -> None:
    """Realize a partimento as SATB, save to a versioned chain file or flat file, and update metadata."""
    log_step(f"\n🎼 Realizing partimento from {args.input}...")
    realized_data = realize.realize_partimento_satb(args.input, call_llm)
    log_step("\n✅ Realized partimento:", color=Fore.GREEN)
    logger.info(json.dumps(realized_data, indent=2))

    # Determine output path and whether it's a "chain" directory
    if args.output and is_likely_directory(args.output):
        chain_dir = Path(args.output)
        chain_dir.mkdir(parents=True, exist_ok=True)
        # Use next versioned filename for realization: realized_01.json, realized_02.json, etc.
        realized_path = get_next_versioned_filename(str(chain_dir), "realized")
        is_chain = True
    else:
        Path("generated/json").mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        realized_path = (
            args.output or f"generated/json/realized_partimento_{timestamp}.json"
        )
        is_chain = False

    # Load partimento.json as full metadata-wrapped source and extract values
    if Path(args.input).exists():
        with open(args.input, "r") as f:
            source_data = json.load(f)
        source = args.input
        prompt = source_data.get("user_prompt") or source_data.get("prompt")
    else:
        source = args.input
        prompt = None

    # Write realization JSON using helper
    write_chain_json(
        realized_data,
        realized_path,
        mode="realize-partimento",
        source_path=source,
        prompt=prompt,
    )
    log_step(f"\n💾 Saved to {realized_path}", color=Fore.YELLOW)

    # Write metadata.json and copy original partimento if using a chain directory
    if is_chain:
        # Always create/copy partimento as partimento_01.json if not present
        partimento_chain_path = chain_dir / "partimento_01.json"
        if not partimento_chain_path.exists():
            if Path(args.input).exists():
                with open(args.input, "r") as f:
                    part_data = json.load(f)
                # If input is a chain-wrapped file, extract "data" if present
                data_to_write = part_data.get("data", part_data)
                write_chain_json(
                    data_to_write,
                    partimento_chain_path,
                    mode="partimento",
                    source_path=source,
                    prompt=prompt,
                )
        # Write metadata.json with zero-padded references
        realized_basename = Path(realized_path).name
        partimento_basename = partimento_chain_path.name
        meta = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "mode": "realize-partimento",
            "source_file": args.input,
            "realized_file": realized_basename,
            "partimento_file": partimento_basename,
            "version": "0.1.0",
        }
        write_metadata(chain_dir, meta)


def handle_export_partimento(args: Namespace) -> None:
    """Export a partimento JSON file to MusicXML, MIDI, and OGG. Chain-aware if given a directory."""
    logger.info(f"\n🎼 Exporting partimento JSON from {args.input}...")

    if args.output and not Path(args.output).suffix:
        Path(args.output).mkdir(parents=True, exist_ok=True)
        musicxml_path = Path(args.output) / "partimento.musicxml"
        midi_path = Path(args.output) / "partimento.mid"
    else:
        base = args.output or args.input
        stem = Path(base).with_suffix("")
        musicxml_path = stem.with_suffix(".musicxml")
        midi_path = stem.with_suffix(".mid")

    logger.info(f"  ➤ Exporting MusicXML to {musicxml_path} ...")
    export_partimento_to_musicxml(args.input, str(musicxml_path))
    logger.info(f"🎼 MusicXML saved to {musicxml_path}")
    logger.info(f"  ➤ Exporting MIDI to {midi_path} ...")
    export_partimento_to_midi(args.input, str(midi_path))
    logger.info(f"🎧 MIDI saved to {midi_path}")

    # Export OGG audio
    ogg_path = Path(midi_path).with_suffix(".ogg")
    log_step(f"  ➤ Converting MIDI to OGG: {ogg_path}")
    export_ogg_from_midi(str(midi_path), str(ogg_path))


def handle_export_realization(args: Namespace) -> None:
    """Export a realized SATB JSON file to MusicXML, MIDI, and OGG. Chain-aware if given a directory."""
    log_step(f"\n🎼 Exporting realized partimento JSON from {args.input}...")

    if args.output and is_likely_directory(args.output):
        Path(args.output).mkdir(parents=True, exist_ok=True)
        musicxml_path = Path(args.output) / "realized.musicxml"
        midi_path = Path(args.output) / "realized.mid"
    else:
        base = args.output or args.input
        stem = Path(base).with_suffix("")
        musicxml_path = stem.with_suffix(".musicxml")
        midi_path = stem.with_suffix(".mid")

    log_step(f"  ➤ Exporting MusicXML to {musicxml_path} ...")
    export_realized_partimento_to_musicxml(args.input, str(musicxml_path))
    log_step(f"🎼 MusicXML saved to {musicxml_path}", color=Fore.YELLOW)
    log_step(f"  ➤ Exporting MIDI to {midi_path} ...")
    export_realized_partimento_to_midi(args.input, str(midi_path))
    log_step(f"🎧 MIDI saved to {midi_path}", color=Fore.YELLOW)
    # Export OGG audio
    ogg_path = Path(midi_path).with_suffix(".ogg")
    log_step(f"  ➤ Converting MIDI to OGG: {ogg_path}")
    export_ogg_from_midi(str(midi_path), str(ogg_path))


# === REVIEW AND REVISE ===
# Includes functions to review partimenti and SATB realizations, and to apply patches.


def handle_review_realization(args: Namespace) -> None:
    """Run LLM review of a realized SATB partimento, save review in chain or flat output, and update metadata if in a chain."""
    log_step(f"\n🔍 Reviewing realized partimento from {args.input}...")
    review_json = review_realized_score(args.input, call_llm)
    review_data = json.loads(review_json)

    # Determine output path: use chain helpers if directory, else timestamped flat file
    if args.output and is_likely_directory(args.output):
        chain_dir = Path(args.output)
        chain_dir.mkdir(parents=True, exist_ok=True)
        output_path = get_next_versioned_filename(str(chain_dir), "review_realization")
        is_chain = True
    else:
        Path("generated/review").mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = args.output or f"generated/review/review_{timestamp}.json"
        is_chain = False

    write_chain_json(
        review_data, output_path, mode="review-score", source_path=args.input
    )

    log_step(f"\n✅ Review saved to {output_path}", color=Fore.GREEN)
    log_step("\n💬 Summary:", color=Fore.YELLOW)
    logger.info(
        Fore.GREEN
        + review_data.get("message", "No review message provided.")
        + Style.RESET_ALL
    )
    strengths = review_data.get("strengths", [])
    if strengths:
        logger.info(Fore.YELLOW + "\nStrengths:" + Style.RESET_ALL)
        for s in strengths:
            logger.info(Fore.YELLOW + f"- {s}" + Style.RESET_ALL)

    issues = review_data.get("issues", [])
    if issues:
        logger.warning(Fore.RED + "\nIssues:" + Style.RESET_ALL)
        for i in issues:
            logger.warning(Fore.RED + f"- {i}" + Style.RESET_ALL)

    # Write metadata.json if using a chain directory
    if is_chain:
        meta = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "mode": "review-score",
            "source_file": args.input,
            "review_file": Path(output_path).name,
            "version": "0.1.0",
        }
        write_metadata(chain_dir, meta)


def handle_review_partimento(args: Namespace) -> None:
    """Run LLM review of a partimento (not yet realized), save review in chain or flat output, and update metadata if in a chain."""
    log_step(f"\n🔍 Reviewing partimento from {args.input}...")
    review_json = review_partimento(args.input, call_llm)
    review_data = json.loads(review_json)

    # Determine output path: use chain helpers if directory, else timestamped flat file
    if args.output and is_likely_directory(args.output):
        chain_dir = Path(args.output)
        chain_dir.mkdir(parents=True, exist_ok=True)
        output_path = get_next_versioned_filename(str(chain_dir), "review_partimento")
        is_chain = True
    else:
        Path("generated/review").mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = args.output or f"generated/review/review_{timestamp}.json"
        is_chain = False

    write_chain_json(
        review_data, output_path, mode="review-partimento", source_path=args.input
    )

    log_step(f"\n✅ Review saved to {output_path}", color=Fore.GREEN)
    log_step("\n💬 Summary:", color=Fore.YELLOW)
    logger.info(
        Fore.GREEN
        + review_data.get("message", "No review message provided.")
        + Style.RESET_ALL
    )

    strengths = review_data.get("strengths", [])
    if strengths:
        logger.info(Fore.YELLOW + "\nStrengths:" + Style.RESET_ALL)
        for s in strengths:
            logger.info(Fore.YELLOW + f"- {s}" + Style.RESET_ALL)

    issues = review_data.get("issues", [])
    if issues:
        logger.warning(Fore.RED + "\nIssues:" + Style.RESET_ALL)
        for i in issues:
            logger.warning(Fore.RED + f"- {i}" + Style.RESET_ALL)

    # Write metadata.json if using a chain directory
    if is_chain:
        meta = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "mode": "review-partimento",
            "source_file": args.input,
            "review_file": Path(output_path).name,
            "version": "0.1.0",
        }
        write_metadata(chain_dir, meta)


def handle_revise_realization(args: Namespace) -> None:
    """Apply a patch from a review file to a realization JSON, save as a new chain version or flat file."""
    log_step(f"\n🔧 Revising realization based on patch...")

    with open(args.input, "r") as f:
        original = json.load(f)

    with open(args.patch, "r") as f:
        review = json.load(f)

    patch = review.get("data", {}).get("suggested_patch")
    if not patch:
        logger.error(
            Fore.RED + "❌ No suggested_patch found in review file." + Style.RESET_ALL
        )
        return

    updated_data = apply_patch(original["data"], patch)

    # Determine output path: use chain helpers if directory, else timestamped flat file
    if args.output and is_likely_directory(args.output):
        chain_dir = Path(args.output)
        chain_dir.mkdir(parents=True, exist_ok=True)
        output_path = get_next_versioned_filename(str(chain_dir), "realized")
    else:
        Path("generated/json").mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = (
            args.output or f"generated/json/revised_realization_{timestamp}.json"
        )

    write_chain_json(
        updated_data, output_path, mode="revise-realization", source_path=args.input
    )

    log_step(f"\n✅ Revised realization saved to {output_path}", color=Fore.YELLOW)


def handler_revise_partimento(args: Namespace) -> None:
    """Apply a patch from a review file to a partimento JSON, save as a new chain version or flat file."""
    log_step(f"\n🔧 Revising partimento based on patch...")

    with open(args.input, "r") as f:
        original = json.load(f)

    with open(args.patch, "r") as f:
        review = json.load(f)

    patch = review.get("data", {}).get("suggested_patch")
    if not patch:
        logger.error(
            Fore.RED + "❌ No suggested_patch found in review file." + Style.RESET_ALL
        )
        return

    updated_data = apply_patch(original["data"], patch)

    # Determine output path: use chain helpers if directory, else timestamped flat file
    if args.output and is_likely_directory(args.output):
        chain_dir = Path(args.output)
        chain_dir.mkdir(parents=True, exist_ok=True)
        output_path = get_next_versioned_filename(str(chain_dir), "partimento")
    else:
        Path("generated/json").mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = (
            args.output or f"generated/json/revised_partimento_{timestamp}.json"
        )

    write_chain_json(
        updated_data, output_path, mode="revise-partimento", source_path=args.input
    )

    log_step(f"\n✅ Revised partimento saved to {output_path}", color=Fore.YELLOW)


handler_map = {
    # full chains
    "chain-realization": handle_chain_partimento_realization,
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
