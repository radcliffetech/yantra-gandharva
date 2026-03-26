"""
Algorithmic jazz lead sheet generation using templates.

Parses natural language prompts for key, form, and style,
then assembles a lead sheet from pre-built chord/melody templates.
"""

import re

from .templates import TEMPLATES, transpose_chords, transpose_melody


def generate_jazz_lead_sheet(prompt: str) -> dict:
    """Generate a jazz lead sheet from a natural language prompt.

    Args:
        prompt: e.g. "12-bar blues in F" or "rhythm changes in Bb"

    Returns:
        dict matching the jazz JSON contract:
        {title, key, meter, melody, chords}
    """
    params = _parse_prompt(prompt)

    template_fn = TEMPLATES.get(params["form"], TEMPLATES["blues"])
    template = template_fn()

    chords = template["chords"]
    melody = template["melody"]

    # Transpose from reference key to target
    if params["key"] != template["ref_key"]:
        chords = transpose_chords(chords, template["ref_key"], params["key"])
        melody = transpose_melody(melody, template["ref_key"], params["key"])

    # Trim or repeat to target bar count if specified
    target_bars = params.get("bars")
    if target_bars and target_bars != len(chords):
        chords, melody = _fit_to_length(chords, melody, target_bars)

    title = _generate_title(params, template)

    return {
        "title": title,
        "key": params["key"],
        "meter": params["meter"],
        "melody": melody,
        "chords": chords,
    }


def _parse_prompt(prompt: str) -> dict:
    """Extract key, form, meter, and bar count from prompt."""
    text = prompt.lower()

    return {
        "key": _parse_key(prompt),
        "form": _parse_form(text),
        "meter": _parse_meter(text),
        "bars": _parse_bars(text),
    }


def _parse_key(prompt: str) -> str:
    """Extract key from prompt. Defaults to C."""
    # Match "in X" pattern where X is a note letter with optional accidental
    m = re.search(
        r"\bin\s+([A-Ga-g][#b♯♭-]?)",
        prompt,
        re.IGNORECASE,
    )
    if m:
        key_str = m.group(1)
        key_str = key_str[0].upper() + key_str[1:]
        key_str = key_str.replace("♯", "#").replace("♭", "-")
        return key_str
    return "C"


def _parse_form(text: str) -> str:
    """Extract form/template from prompt."""
    if any(w in text for w in ["rhythm change", "rhythm changes", "aaba"]):
        return "rhythm_changes"
    if "minor blues" in text or "minor blue" in text:
        return "minor_blues"
    if "blues" in text or "12-bar" in text or "12 bar" in text:
        return "blues"
    if "standard" in text or "16-bar" in text or "16 bar" in text:
        return "standard_16"
    if "turnaround" in text or "ii-v-i" in text or "ii v i" in text:
        return "turnaround"
    if "ii-v" in text or "ii v" in text:
        return "ii_v_i"
    return "blues"


def _parse_meter(text: str) -> str:
    """Extract time signature. Defaults to 4/4."""
    m = re.search(r"(\d+/\d+)", text)
    if m:
        return m.group(1)
    if "waltz" in text or "3/4" in text:
        return "3/4"
    return "4/4"


def _parse_bars(text: str) -> int | None:
    """Extract bar count if specified. Returns None for template default."""
    m = re.search(r"(\d+)\s*(?:bars?|measures?)", text)
    if m:
        n = int(m.group(1))
        if 2 <= n <= 64:
            return n
    return None


def _fit_to_length(chords, melody, target_bars):
    """Trim or repeat to hit target bar count."""
    if len(chords) >= target_bars:
        return chords[:target_bars], melody[:target_bars]

    # Repeat pattern to fill
    result_chords = []
    result_melody = []
    while len(result_chords) < target_bars:
        result_chords.extend(chords)
        result_melody.extend(melody)
    return result_chords[:target_bars], result_melody[:target_bars]


def _generate_title(params, template):
    """Generate a descriptive title."""
    form_names = {
        "blues": "Blues",
        "minor_blues": "Minor Blues",
        "rhythm_changes": "Rhythm Changes",
        "standard_16": "Standard",
        "turnaround": "Turnaround",
        "ii_v_i": "ii-V-I",
    }
    form_name = form_names.get(params["form"], template.get("form", "Lead Sheet"))
    return f"{form_name} in {params['key']}"
