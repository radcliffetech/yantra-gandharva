"""
Algorithmic review of partimenti and SATB realizations.

Rule-based analysis producing structured review JSON compatible
with the LLM review output format. Extends the existing lint_satb()
with additional checks for partimento-specific concerns.
"""

import json
import logging

from music21 import interval, pitch

logger = logging.getLogger(__name__)


def review_partimento(json_path: str) -> str:
    """Review a partimento bassline for compositional issues.

    Args:
        json_path: Path to a chain-wrapped partimento JSON file.

    Returns:
        JSON string matching the review contract:
        {message, strengths, issues, suggested_patch?}
    """
    with open(json_path, "r") as f:
        raw = json.load(f)
    data = raw.get("data", raw)

    bassline = data.get("bassline", [])
    figures = data.get("figures", [])
    cadences = data.get("cadences", [])
    key_str = data.get("key", "C major")

    issues = []
    strengths = []

    # Normalize flat bassline
    if bassline and isinstance(bassline[0], str):
        bassline = [[n] for n in bassline]

    flat_bass = [n for measure in bassline for n in measure]

    # 1. Check for awkward leaps (> octave)
    for i in range(1, len(flat_bass)):
        try:
            p1 = pitch.Pitch(flat_bass[i - 1])
            p2 = pitch.Pitch(flat_bass[i])
            ivl = interval.Interval(p1, p2)
            semitones = abs(ivl.semitones)
            if semitones > 12:
                issues.append(
                    f"Awkward leap of {ivl.directedName} between "
                    f"notes {i} and {i+1} ({flat_bass[i-1]} to {flat_bass[i]})"
                )
        except Exception:
            pass

    # 2. Check bass range (E2 to C4)
    for i, note_str in enumerate(flat_bass):
        try:
            p = pitch.Pitch(note_str)
            if p < pitch.Pitch("E2") or p > pitch.Pitch("C4"):
                measure_idx = _note_to_measure(i, bassline)
                issues.append(
                    f"Bass note {note_str} in measure {measure_idx + 1} out of range [E2-C4]"
                )
        except Exception:
            pass

    # 3. Check for cadences
    if not cadences:
        issues.append("No cadences marked — partimento should have at least one cadence")
    else:
        has_final = any(
            "authentic" in c.lower() or "plagal" in c.lower() for c in cadences
        )
        if not has_final:
            issues.append(
                "No authentic or plagal cadence found — "
                "partimento typically ends with a strong cadence"
            )

    # 4. Check for monotony (same note repeated > 3 times consecutively)
    for i in range(len(flat_bass) - 3):
        if len(set(flat_bass[i : i + 4])) == 1:
            measure_idx = _note_to_measure(i, bassline)
            issues.append(
                f"Monotonous repetition of {flat_bass[i]} "
                f"starting at measure {measure_idx + 1}"
            )
            break  # Only report once

    # 5. Check figures consistency
    if figures:
        if len(figures) != len(bassline):
            issues.append(
                f"Figures length ({len(figures)}) doesn't match "
                f"bassline length ({len(bassline)})"
            )

    # Strengths
    if len(flat_bass) >= 4:
        # Check for stepwise motion (mostly stepwise is good)
        step_count = 0
        for i in range(1, len(flat_bass)):
            try:
                p1 = pitch.Pitch(flat_bass[i - 1])
                p2 = pitch.Pitch(flat_bass[i])
                ivl = interval.Interval(p1, p2)
                if abs(ivl.semitones) <= 2:
                    step_count += 1
            except Exception:
                pass
        if step_count >= len(flat_bass) * 0.4:
            strengths.append(
                {"aspect": "melodic contour", "description": "Good stepwise motion in the bass"}
            )

    if cadences:
        strengths.append(
            {"aspect": "cadential structure", "description": f"{len(cadences)} cadence(s) marked"}
        )

    if not issues:
        strengths.append(
            {
                "aspect": "overall quality",
                "description": "No compositional issues detected",
            }
        )

    # Build message
    if issues:
        message = f"Found {len(issues)} issue(s) in the partimento. " + issues[0]
    else:
        message = "Partimento is well-constructed with no obvious issues."

    result = {
        "message": message,
        "strengths": strengths,
        "issues": issues,
    }

    return json.dumps(result)


def review_realized_score(json_path: str) -> str:
    """Review a realized SATB score for voice-leading issues.

    Extends the existing lint_satb() with additional checks:
    - Voice crossing detection
    - Spacing violations (> octave between adjacent upper voices)
    - Doubled leading tone detection
    - Range checking for all voices

    Args:
        json_path: Path to a chain-wrapped realized SATB JSON file.

    Returns:
        JSON string matching the review contract.
    """
    with open(json_path, "r") as f:
        raw = json.load(f)
    data = raw.get("data", raw)

    issues = []
    strengths = []
    suggested_patch = {}

    voices = {}
    for voice_name in ["soprano", "alto", "tenor", "bass"]:
        voice_data = data.get(voice_name, [])
        # Flatten to list of pitch strings per measure
        voices[voice_name] = voice_data

    # Flatten all voices for note-by-note analysis
    flat = {}
    for voice_name in ["soprano", "alto", "tenor", "bass"]:
        flat[voice_name] = [n for measure in voices[voice_name] for n in measure]

    num_notes = min(len(v) for v in flat.values()) if flat.values() else 0

    # 1. Range checking
    RANGES = {
        "soprano": (pitch.Pitch("C4"), pitch.Pitch("A5")),
        "alto": (pitch.Pitch("G3"), pitch.Pitch("E5")),
        "tenor": (pitch.Pitch("C3"), pitch.Pitch("A4")),
        "bass": (pitch.Pitch("E2"), pitch.Pitch("E4")),
    }
    for voice_name, (low, high) in RANGES.items():
        for i, note_str in enumerate(flat[voice_name]):
            try:
                p = pitch.Pitch(note_str)
                if p < low or p > high:
                    measure_idx = _note_to_measure_from_voice(i, voices[voice_name])
                    issues.append(
                        f"{voice_name.capitalize()} m{measure_idx + 1}: "
                        f"{note_str} out of range [{low.nameWithOctave}-{high.nameWithOctave}]"
                    )
            except Exception:
                pass

    # 2. Voice crossing detection
    voice_order = ["soprano", "alto", "tenor", "bass"]
    for idx in range(len(voice_order) - 1):
        upper_name = voice_order[idx]
        lower_name = voice_order[idx + 1]
        for i in range(num_notes):
            try:
                upper_p = pitch.Pitch(flat[upper_name][i])
                lower_p = pitch.Pitch(flat[lower_name][i])
                if upper_p < lower_p:
                    measure_idx = _note_to_measure_from_voice(
                        i, voices[upper_name]
                    )
                    issues.append(
                        f"Voice crossing: {upper_name.capitalize()} "
                        f"({flat[upper_name][i]}) below "
                        f"{lower_name.capitalize()} ({flat[lower_name][i]}) "
                        f"at m{measure_idx + 1}"
                    )
            except Exception:
                pass

    # 3. Spacing violations (> octave between adjacent upper voices)
    upper_pairs = [("soprano", "alto"), ("alto", "tenor")]
    for upper_name, lower_name in upper_pairs:
        for i in range(num_notes):
            try:
                upper_p = pitch.Pitch(flat[upper_name][i])
                lower_p = pitch.Pitch(flat[lower_name][i])
                ivl = interval.Interval(lower_p, upper_p)
                if ivl.semitones > 12:
                    measure_idx = _note_to_measure_from_voice(
                        i, voices[upper_name]
                    )
                    issues.append(
                        f"Spacing: > octave between {upper_name.capitalize()} "
                        f"and {lower_name.capitalize()} at m{measure_idx + 1}"
                    )
            except Exception:
                pass

    # 4. Parallel 5ths and 8ves between all voice pairs
    pair_checks = [
        ("soprano", "alto"),
        ("soprano", "tenor"),
        ("soprano", "bass"),
        ("alto", "tenor"),
        ("alto", "bass"),
        ("tenor", "bass"),
    ]
    for v1_name, v2_name in pair_checks:
        for i in range(num_notes - 1):
            try:
                v1_a = pitch.Pitch(flat[v1_name][i])
                v1_b = pitch.Pitch(flat[v1_name][i + 1])
                v2_a = pitch.Pitch(flat[v2_name][i])
                v2_b = pitch.Pitch(flat[v2_name][i + 1])

                ivl_a = interval.Interval(v2_a, v1_a)
                ivl_b = interval.Interval(v2_b, v1_b)

                # Check for parallel perfect intervals
                if ivl_a.simpleName == ivl_b.simpleName and ivl_a.simpleName in (
                    "P5",
                    "P8",
                    "P1",
                ):
                    # Confirm both voices actually moved (not oblique motion)
                    if v1_a != v1_b and v2_a != v2_b:
                        measure_idx = _note_to_measure_from_voice(
                            i, voices[v1_name]
                        )
                        issues.append(
                            f"Parallel {ivl_a.simpleName}: "
                            f"{v1_name.capitalize()}/{v2_name.capitalize()} "
                            f"at m{measure_idx + 1}-{measure_idx + 2}"
                        )
            except Exception:
                pass

    # 5. Doubled leading tone
    key_str = data.get("key", "C major")
    leading_tone = _get_leading_tone(key_str)
    if leading_tone:
        for i in range(num_notes):
            lt_count = 0
            for voice_name in voice_order:
                try:
                    p = pitch.Pitch(flat[voice_name][i])
                    if p.name == leading_tone:
                        lt_count += 1
                except Exception:
                    pass
            if lt_count > 1:
                measure_idx = _note_to_measure_from_voice(i, voices["soprano"])
                issues.append(f"Doubled leading tone ({leading_tone}) at m{measure_idx + 1}")

    # Strengths
    if not any("crossing" in i.lower() for i in issues):
        strengths.append(
            {"aspect": "voice independence", "description": "No voice crossing detected"}
        )
    if not any("parallel" in i.lower() for i in issues):
        strengths.append(
            {"aspect": "voice leading", "description": "No parallel 5ths or 8ves detected"}
        )
    if not any("range" in i.lower() for i in issues):
        strengths.append(
            {"aspect": "voice ranges", "description": "All voices within standard ranges"}
        )
    if not issues:
        strengths.append(
            {"aspect": "overall quality", "description": "No voice-leading issues detected"}
        )

    # Build message
    if issues:
        message = f"Found {len(issues)} voice-leading issue(s). " + issues[0]
    else:
        message = "Realization is clean with no voice-leading violations."

    result = {
        "message": message,
        "strengths": strengths,
        "issues": issues,
    }

    # Add suggested_patch if there are fixable issues
    if issues:
        result["suggested_patch"] = suggested_patch if suggested_patch else {}

    return json.dumps(result)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _note_to_measure(flat_index, bassline):
    """Convert a flat note index to a measure index."""
    count = 0
    for m_idx, measure in enumerate(bassline):
        count += len(measure)
        if flat_index < count:
            return m_idx
    return len(bassline) - 1


def _note_to_measure_from_voice(flat_index, voice_measures):
    """Convert a flat note index to a measure index for a voice."""
    count = 0
    for m_idx, measure in enumerate(voice_measures):
        count += len(measure)
        if flat_index < count:
            return m_idx
    return len(voice_measures) - 1


def _get_leading_tone(key_str):
    """Get the leading tone pitch name for a key string."""
    try:
        from music21 import key as m21_key

        parts = key_str.split()
        tonic = parts[0]
        mode = parts[1] if len(parts) > 1 else "major"
        k = m21_key.Key(tonic, mode)
        lt = k.pitchFromDegree(7)
        return lt.name
    except Exception:
        return None
