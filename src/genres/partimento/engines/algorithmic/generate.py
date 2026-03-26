"""
Algorithmic partimento generation using schemata assembly.

Assembles a partimento bassline from a library of Galant schemata,
parsed from a natural language prompt. No LLM required.
"""

import random

from music21 import pitch

from . import schemata
from .prompt_parser import parse_prompt

# Bass octave range for generated notes
BASS_OCTAVE_LOW = 2
BASS_OCTAVE_HIGH = 3


def generate_partimento(prompt: str) -> dict:
    """Generate a partimento from a natural language prompt using rule-based assembly.

    Args:
        prompt: e.g. "8 bars in D minor, Romanesca then Prinner, end with PAC"

    Returns:
        dict matching the partimento JSON contract:
        {title, key, bassline, figures, cadences, style, modulations}
    """
    params = parse_prompt(prompt)
    target_key = params["key"]
    target_bars = params["bars"]
    style = params["style"]
    cadence_type = params["cadence_type"]
    requested_schemata = params["schemata"]

    # Build the sequence of schema patterns to use
    pattern_sequence = _plan_patterns(requested_schemata, target_bars, cadence_type)

    # Assemble bassline and figures from patterns
    bassline = []
    figures = []
    cadences = []
    bar_offset = 0

    for pattern_name in pattern_sequence:
        schema_fn = schemata.SCHEMATA[pattern_name]
        pattern = schema_fn(target_key)

        for i, bass_note_name in enumerate(pattern["bass"]):
            note_str = _assign_octave(bass_note_name)
            bassline.append([note_str])
            figures.append([pattern["figures"][i]])

        if pattern["cadence"]:
            cadence_bar = bar_offset + pattern["bars"]
            cadences.append(f"measure {cadence_bar}: {pattern['cadence']}")

        bar_offset += pattern["bars"]

    # Trim or pad to exact bar count
    bassline, figures, cadences = _fit_to_length(
        bassline, figures, cadences, target_bars, target_key
    )

    key_str = f"{target_key.tonic.name} {target_key.mode}"

    return {
        "title": f"Partimento in {target_key.tonic.name}",
        "key": key_str,
        "bassline": bassline,
        "figures": figures,
        "cadences": cadences,
        "style": f"{style} (algorithmic)",
        "modulations": [],
    }


def _plan_patterns(requested_schemata, target_bars, cadence_type):
    """Plan which schemata to use and in what order.

    Strategy:
    1. Use explicitly requested schemata first.
    2. Fill remaining bars with body schemata.
    3. Always end with a cadence.
    """
    cadence_map = {
        "authentic": "cadence_authentic",
        "half": "cadence_half",
        "deceptive": "cadence_deceptive",
        "plagal": "cadence_plagal",
    }
    final_cadence = cadence_map.get(cadence_type, "cadence_authentic")

    # Reserve 2 bars for the final cadence
    available_bars = target_bars - 2

    sequence = []
    bars_used = 0

    # Add requested schemata
    for name in requested_schemata:
        schema_fn = schemata.SCHEMATA.get(name)
        if schema_fn:
            pattern = schema_fn()
            if bars_used + pattern["bars"] <= available_bars:
                sequence.append(name)
                bars_used += pattern["bars"]

    # Fill remaining with body schemata
    body_options = list(schemata.BODY_SCHEMATA)
    attempts = 0
    while bars_used < available_bars and attempts < 20:
        name = body_options[attempts % len(body_options)]
        pattern = schemata.SCHEMATA[name]()
        if bars_used + pattern["bars"] <= available_bars:
            sequence.append(name)
            bars_used += pattern["bars"]
        attempts += 1

    # Add midpoint cadence for longer pieces
    if target_bars >= 12 and bars_used >= 4:
        # Insert a half cadence roughly in the middle
        mid_point = len(sequence) // 2
        sequence.insert(mid_point, "cadence_half")

    # Always end with cadence
    sequence.append(final_cadence)

    return sequence


def _assign_octave(note_name):
    """Assign an appropriate bass octave to a note name.

    Places notes in octave 2 or 3 to stay within bass range (E2-C4).
    """
    p = pitch.Pitch(note_name)
    p.octave = BASS_OCTAVE_LOW
    # If the note is very low (below E2), bump up
    if p < pitch.Pitch("E2"):
        p.octave = BASS_OCTAVE_HIGH
    return str(p)


def _fit_to_length(bassline, figures, cadences, target_bars, target_key):
    """Trim or pad the assembled pattern to exactly target_bars measures."""
    if len(bassline) > target_bars:
        # Trim from the middle, keeping first few and last (cadence) bars
        keep_end = 2  # cadence bars
        keep_start = target_bars - keep_end
        bassline = bassline[:keep_start] + bassline[-keep_end:]
        figures = figures[:keep_start] + figures[-keep_end:]
        # Recompute cadences for trimmed version
        cadences = [c for c in cadences if _cadence_bar(c) <= target_bars]

    elif len(bassline) < target_bars:
        # Pad with tonic pedal notes before the cadence
        tonic_note = _assign_octave(target_key.tonic.name)
        shortfall = target_bars - len(bassline)
        insert_pos = max(0, len(bassline) - 2)  # before cadence
        for _ in range(shortfall):
            bassline.insert(insert_pos, [tonic_note])
            figures.insert(insert_pos, [["5", "3"]])

    return bassline, figures, cadences


def _cadence_bar(cadence_str):
    """Extract bar number from cadence string like 'measure 4: half cadence'."""
    import re

    m = re.match(r"measure (\d+)", cadence_str)
    return int(m.group(1)) if m else 0
