import logging
import os
import subprocess

from colorama import Fore, Style
from music21 import note, pitch

logger = logging.getLogger(__name__)

RANGE = {
    "s": (pitch.Pitch("C4"), pitch.Pitch("A5")),
    "a": (pitch.Pitch("G3"), pitch.Pitch("D5")),
    "t": (pitch.Pitch("C3"), pitch.Pitch("G4")),
    "b": (pitch.Pitch("E2"), pitch.Pitch("C4")),
}


def in_range(part_name: str, p: pitch.Pitch) -> bool:
    low, high = RANGE[part_name]
    return low <= p <= high


def interval_name(n1: note.Note, n2: note.Note) -> str:
    return n1.pitch.intervalClassString(n2.pitch)


def export_ogg_from_midi(midi_path, ogg_path):
    """Convert a MIDI file to OGG using Timidity and log progress."""
    if os.path.exists(midi_path):
        try:
            subprocess.run(
                ["timidity", midi_path, "-Ow", "-o", ogg_path],
                check=True,
            )
            logger.info(Fore.YELLOW + f"🎧 OGG audio saved to {ogg_path}")
        except FileNotFoundError:
            logger.warning(
                Fore.YELLOW + "⚠️  Timidity not found. Skipping OGG audio export."
            )
    else:
        logger.error(Fore.RED + "❌ MIDI file not found. Cannot convert to OGG.")
