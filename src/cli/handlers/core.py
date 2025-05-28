import json
import os
import subprocess
import sys

from colorama import Fore

from lib.utils.musicxml_utils import load_musicxml


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


def handle_inspect_musicxml(args):
    from lib.utils.musicxml_utils import print_score_summary

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
    "inspect-musicxml": handle_inspect_musicxml,
    "export-audio": handle_write_audio,
}
