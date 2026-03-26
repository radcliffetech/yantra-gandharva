"""
Parse natural language prompts into structured parameters for algorithmic generation.

Extracts key, measure count, style, cadence preferences, and schema requests
using regex. Falls back to sensible defaults when prompt is unparsable.
"""

import re

from music21 import key


def parse_prompt(prompt: str) -> dict:
    """Parse a natural language prompt into generation parameters.

    Args:
        prompt: e.g. "8 bars in D minor, Romanesca then Prinner, end with PAC"

    Returns:
        dict with keys: key, bars, style, schemata, cadence_type
    """
    text = prompt.lower()

    return {
        "key": _parse_key(text, prompt),
        "bars": _parse_bars(text),
        "style": _parse_style(text),
        "schemata": _parse_schemata(text),
        "cadence_type": _parse_cadence(text),
    }


def _parse_key(text: str, original: str) -> key.Key:
    """Extract key from prompt. Defaults to C major."""
    # Try "in X major/minor" pattern (case-insensitive on lowercase text,
    # but use original for note name casing)
    m = re.search(
        r"(?:in\s+)?([A-Ga-g][#b♯♭]?)\s+(major|minor|maj|min)",
        original,
        re.IGNORECASE,
    )
    if m:
        tonic = m.group(1).replace("♯", "#").replace("♭", "b")
        mode = "minor" if m.group(2).lower().startswith("min") else "major"
        return key.Key(tonic, mode)

    # Try just a key letter with sharp/flat, e.g. "in Bb" or "in F#"
    m = re.search(r"\bin\s+([A-Ga-g][#b♯♭]?)\b", original, re.IGNORECASE)
    if m:
        tonic = m.group(1).replace("♯", "#").replace("♭", "b")
        return key.Key(tonic, "major")

    return key.Key("C", "major")


def _parse_bars(text: str) -> int:
    """Extract measure count. Defaults to 8."""
    m = re.search(r"(\d+)\s*(?:bars?|measures?)", text)
    if m:
        n = int(m.group(1))
        if 2 <= n <= 64:
            return n
    return 8


def _parse_style(text: str) -> str:
    """Extract style card name. Defaults to 'Furno'."""
    styles = {
        "furno": "Furno",
        "palestrina": "Palestrina",
        "j.s. bach": "J. S. Bach",
        "j. s. bach": "J. S. Bach",
        "bach": "J. S. Bach",
        "c.p.e. bach": "C. P. E. Bach",
        "c. p. e. bach": "C. P. E. Bach",
    }
    for pattern, name in styles.items():
        if pattern in text:
            return name
    return "Furno"


def _parse_schemata(text: str) -> list:
    """Extract requested schemata names. Returns list of schema keys."""
    schema_names = {
        "romanesca": "romanesca",
        "prinner": "prinner",
        "monte": "monte",
        "fonte": "fonte",
        "rule of the octave": "rule_of_octave_ascending",
        "rule of octave": "rule_of_octave_ascending",
        "ascending octave": "rule_of_octave_ascending",
        "descending octave": "rule_of_octave_descending",
    }
    found = []
    for pattern, schema_key in schema_names.items():
        if pattern in text:
            found.append(schema_key)
    return found


def _parse_cadence(text: str) -> str:
    """Extract cadence type preference. Defaults to 'authentic'."""
    if any(w in text for w in ["half cadence", "hc", "half"]):
        return "half"
    if any(w in text for w in ["deceptive", "dc"]):
        return "deceptive"
    if any(w in text for w in ["plagal", "amen"]):
        return "plagal"
    # Default: authentic
    return "authentic"
