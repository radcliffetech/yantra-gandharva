"""
Algorithmic SATB realization using music21's figuredBass.realizer.

Takes a partimento JSON (bassline + figures) and produces four-part
SATB voice leading using constraint-based realization.
"""

import json
import logging

from music21 import key as m21_key
from music21 import meter, note, pitch
from music21.figuredBass import realizer

logger = logging.getLogger(__name__)


def realize_partimento_satb(json_data) -> dict:
    """Realize a partimento into SATB texture algorithmically.

    Args:
        json_data: Either a dict (partimento data) or a string (JSON or file path).
                   Expected keys: key, bassline, figures

    Returns:
        dict matching the SATB JSON contract:
        {soprano: [[...]], alto: [[...]], tenor: [[...]], bass: [[...]]}
    """
    data = _normalize_input(json_data)

    # Parse key
    key_str = data.get("key", "C major")
    target_key = _parse_key(key_str)

    # Extract bassline and figures
    bassline = data["bassline"]
    figures = data.get("figures", [])

    # Normalize flat bassline to measure-based
    if bassline and isinstance(bassline[0], str):
        bassline = [[n] for n in bassline]

    # Normalize figures to match bassline structure
    if figures and not isinstance(figures[0], list):
        figures = [[f] for f in figures]

    # Build the figured bass line for music21
    progression = _realize_with_music21(bassline, figures, target_key)

    # Convert to output format
    return _format_output(progression, bassline)


def _normalize_input(json_data):
    """Accept dict, JSON string, or file path."""
    if isinstance(json_data, dict):
        return json_data
    if isinstance(json_data, str):
        try:
            return json.loads(json_data)
        except (json.JSONDecodeError, ValueError):
            # Treat as file path
            with open(json_data, "r") as f:
                loaded = json.load(f)
            return loaded.get("data", loaded)
    return json_data


def _parse_key(key_str: str):
    """Parse key string like 'C major' or 'D minor' into music21 Key."""
    parts = key_str.split()
    tonic = parts[0].replace("♯", "#").replace("♭", "b")
    mode = parts[1] if len(parts) > 1 else "major"
    return m21_key.Key(tonic, mode)


def _realize_with_music21(bassline, figures, target_key):
    """Use music21's figuredBass.realizer to generate SATB voices.

    Returns a list of tuples, each containing 4 pitches (S, A, T, B).
    """
    fb_line = realizer.FiguredBassLine(target_key, meter.TimeSignature("4/4"))

    for i, measure_notes in enumerate(bassline):
        note_count = len(measure_notes)
        ql = 4.0 / note_count if note_count > 0 else 4.0

        for j, note_str in enumerate(measure_notes):
            clean_note = (
                note_str.replace("♯", "#").replace("♭", "b").replace("♮", "")
            )
            n = note.Note(clean_note, quarterLength=ql)

            # Get figures for this note
            fig_str = _get_figure_string(figures, i, j)
            if fig_str:
                n.addLyric(fig_str)

            fb_line.addElement(n)

    # Realize
    realization = fb_line.realize()
    num_solutions = realization.getNumSolutions()

    if num_solutions == 0:
        logger.warning("No valid realizations found, falling back to simple voicing")
        return _fallback_realization(bassline, target_key)

    # Get a progression — use getAllPossibilityProgressions and pick one
    # (getRandomPossibilityProgression has a Python 3.14 compat issue)
    try:
        progs = realization.getAllPossibilityProgressions()
        # Pick from the middle for a balanced voicing
        prog = progs[len(progs) // 2]
    except Exception:
        logger.warning("Could not get progressions, falling back to simple voicing")
        return _fallback_realization(bassline, target_key)

    return prog


def _get_figure_string(figures, measure_idx, note_idx):
    """Safely extract figure string from nested figures list."""
    if measure_idx >= len(figures):
        return ""
    measure_figs = figures[measure_idx]
    if note_idx >= len(measure_figs):
        return ""
    fig = measure_figs[note_idx]
    if isinstance(fig, list):
        return " ".join(fig)
    return str(fig) if fig else ""


def _format_output(progression, bassline):
    """Convert a progression of (S, A, T, B) tuples into the output JSON format.

    The output mirrors the bassline's measure structure:
    each voice is a list of measures, each measure is a list of note strings.
    """
    soprano = []
    alto = []
    tenor = []
    bass = []

    prog_idx = 0
    for measure_notes in bassline:
        s_measure = []
        a_measure = []
        t_measure = []
        b_measure = []

        for _ in measure_notes:
            if prog_idx < len(progression):
                poss = progression[prog_idx]
                # music21 possibilities are (S, A, T, B) top to bottom
                s_measure.append(str(poss[0]))
                a_measure.append(str(poss[1]))
                t_measure.append(str(poss[2]))
                b_measure.append(str(poss[3]))
                prog_idx += 1
            else:
                # Shouldn't happen, but handle gracefully
                b_note = measure_notes[0] if measure_notes else "C3"
                s_measure.append("C5")
                a_measure.append("E4")
                t_measure.append("G3")
                b_measure.append(b_note)

        soprano.append(s_measure)
        alto.append(a_measure)
        tenor.append(t_measure)
        bass.append(b_measure)

    return {
        "soprano": soprano,
        "alto": alto,
        "tenor": tenor,
        "bass": bass,
    }


def _fallback_realization(bassline, target_key):
    """Simple fallback: generate basic chord tones above each bass note.

    Used when music21's realizer can't find valid voicings.
    Returns a list of (S, A, T, B) pitch tuples.
    """
    result = []
    scale = target_key.getScale()

    for measure_notes in bassline:
        for note_str in measure_notes:
            clean = note_str.replace("♯", "#").replace("♭", "b")
            bass_pitch = pitch.Pitch(clean)

            # Build a simple triad above the bass
            # Find the 3rd and 5th above
            third = bass_pitch.transpose("M3")
            fifth = bass_pitch.transpose("P5")

            # Place voices in appropriate octaves
            tenor_p = pitch.Pitch(third.name)
            tenor_p.octave = 3
            if tenor_p < pitch.Pitch("C3"):
                tenor_p.octave = 4

            alto_p = pitch.Pitch(fifth.name)
            alto_p.octave = 4

            soprano_p = pitch.Pitch(bass_pitch.name)
            soprano_p.octave = 5
            if soprano_p > pitch.Pitch("A5"):
                soprano_p.octave = 4

            result.append((soprano_p, alto_p, tenor_p, bass_pitch))

    return result
