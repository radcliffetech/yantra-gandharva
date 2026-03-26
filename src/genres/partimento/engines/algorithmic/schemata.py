"""
Partimento schemata library — pre-composed bass patterns from the Galant tradition.

Each schema function returns a dict with:
  - bass: list of note name strings (without octave), e.g. ["C", "B", "A", "G"]
  - figures: parallel list of figure lists, e.g. [["5","3"], ["6"], [], ["5","3"]]
  - bars: number of measures this pattern spans
  - cadence: optional cadence label or None

All patterns are in C major / A minor as reference key.
Transposition to the target key is handled by the caller.
"""

from music21 import interval, key, pitch


# ---------------------------------------------------------------------------
# Transposition helper
# ---------------------------------------------------------------------------


def transpose_pattern(bass_notes, from_key, to_key):
    """Transpose a list of note-name strings from one key to another.

    Uses scale-degree mapping so that patterns respect the target key's
    mode (e.g. C major → D minor uses D minor scale, not D major).

    Args:
        bass_notes: list of note names without octave, e.g. ["C", "D", "E"]
        from_key: key.Key to transpose from (reference key)
        to_key: key.Key to transpose to (target key)

    Returns:
        list of transposed note name strings
    """
    # Build scale-degree lookup for the source key
    from_scale = from_key.getScale()
    from_pitches = [p.name for p in from_scale.getPitches(
        from_key.tonic.name + "2", from_key.tonic.name + "3"
    )]

    to_scale = to_key.getScale()
    to_pitches = [p.name for p in to_scale.getPitches(
        to_key.tonic.name + "2", to_key.tonic.name + "3"
    )]

    # Map source scale degrees to target scale degrees
    degree_map = {}
    for i in range(min(len(from_pitches), len(to_pitches))):
        degree_map[from_pitches[i]] = to_pitches[i]

    # For chromatic notes not in the source scale, fall back to interval transposition
    trans_interval = interval.Interval(
        noteStart=pitch.Pitch(from_key.tonic.name),
        noteEnd=pitch.Pitch(to_key.tonic.name),
    )

    result = []
    for n in bass_notes:
        if n in degree_map:
            result.append(degree_map[n])
        else:
            # Chromatic note — use interval transposition
            p = pitch.Pitch(n)
            p = p.transpose(trans_interval)
            result.append(p.name)
    return result


# ---------------------------------------------------------------------------
# Schema definitions (all in C major reference key)
# ---------------------------------------------------------------------------

REF_KEY = key.Key("C", "major")
REF_KEY_MINOR = key.Key("A", "minor")


def romanesca(target_key=None):
    """Romanesca: I-V-vi-III descending bass, 4 bars.

    Classic galant schema: descending thirds in the bass.
    """
    bass = ["C", "B", "A", "G"]
    figures = [["5", "3"], ["6"], ["5", "3"], ["6"]]
    if target_key and target_key.tonic.name != "C":
        bass = transpose_pattern(bass, REF_KEY, target_key)
    return {
        "bass": bass,
        "figures": figures,
        "bars": 4,
        "cadence": None,
    }


def prinner(target_key=None):
    """Prinner: 6-5-4-3 descending, 4 bars.

    A riposte schema, often answering an opening gambit.
    Bass descends stepwise: A-G-F-E in C major (scale degrees 6-5-4-3).
    """
    bass = ["A", "G", "F", "E"]
    figures = [["5", "3"], ["5", "3"], ["6"], ["6"]]
    if target_key and target_key.tonic.name != "C":
        bass = transpose_pattern(bass, REF_KEY, target_key)
    return {
        "bass": bass,
        "figures": figures,
        "bars": 4,
        "cadence": None,
    }


def monte(target_key=None):
    """Monte: ascending sequence, 4 bars.

    Rising sequence: ii-V / iii-vi pattern.
    Bass: D-G-E-A in C major.
    """
    bass = ["D", "G", "E", "A"]
    figures = [["5", "3"], ["5", "3"], ["6"], ["5", "3"]]
    if target_key and target_key.tonic.name != "C":
        bass = transpose_pattern(bass, REF_KEY, target_key)
    return {
        "bass": bass,
        "figures": figures,
        "bars": 4,
        "cadence": None,
    }


def fonte(target_key=None):
    """Fonte: descending sequence from minor, 4 bars.

    Descending sequence: typically from vi area.
    Bass: A-D-G-C in C major (descending fifths).
    """
    bass = ["A", "D", "G", "C"]
    figures = [["5", "3"], ["5", "3"], ["5", "3"], ["5", "3"]]
    if target_key and target_key.tonic.name != "C":
        bass = transpose_pattern(bass, REF_KEY, target_key)
    return {
        "bass": bass,
        "figures": figures,
        "bars": 4,
        "cadence": None,
    }


def rule_of_octave_ascending(target_key=None):
    """Rule of the Octave (ascending): 8 bars, one bass note per bar.

    The fundamental pedagogical pattern of the partimento tradition.
    Ascending scale in the bass with standard harmonization.
    """
    bass = ["C", "D", "E", "F", "G", "A", "B", "C"]
    figures = [
        ["5", "3"],  # I
        ["6"],  # passing
        ["6"],  # I6
        ["5", "3"],  # IV
        ["5", "3"],  # V
        ["6"],  # vi or IV6
        ["6"],  # viio6
        ["5", "3"],  # I
    ]
    if target_key and target_key.tonic.name != "C":
        bass = transpose_pattern(bass, REF_KEY, target_key)
    return {
        "bass": bass,
        "figures": figures,
        "bars": 8,
        "cadence": None,
    }


def rule_of_octave_descending(target_key=None):
    """Rule of the Octave (descending): 8 bars.

    Descending scale in the bass with standard harmonization.
    """
    bass = ["C", "B", "A", "G", "F", "E", "D", "C"]
    figures = [
        ["5", "3"],  # I (upper octave)
        ["6"],  # viio6
        ["6"],  # vi or IV6
        ["5", "3"],  # V
        ["6"],  # IV6
        ["6"],  # I6
        ["6"],  # passing
        ["5", "3"],  # I
    ]
    if target_key and target_key.tonic.name != "C":
        bass = transpose_pattern(bass, REF_KEY, target_key)
    return {
        "bass": bass,
        "figures": figures,
        "bars": 8,
        "cadence": None,
    }


def cadence_authentic(target_key=None):
    """Authentic cadence (PAC): V-I, 2 bars."""
    bass = ["G", "C"]
    figures = [["5", "3"], ["5", "3"]]
    if target_key and target_key.tonic.name != "C":
        bass = transpose_pattern(bass, REF_KEY, target_key)
    return {
        "bass": bass,
        "figures": figures,
        "bars": 2,
        "cadence": "authentic cadence",
    }


def cadence_half(target_key=None):
    """Half cadence: I-V, 2 bars."""
    bass = ["C", "G"]
    figures = [["5", "3"], ["5", "3"]]
    if target_key and target_key.tonic.name != "C":
        bass = transpose_pattern(bass, REF_KEY, target_key)
    return {
        "bass": bass,
        "figures": figures,
        "bars": 2,
        "cadence": "half cadence",
    }


def cadence_deceptive(target_key=None):
    """Deceptive cadence: V-vi, 2 bars."""
    bass = ["G", "A"]
    figures = [["5", "3"], ["5", "3"]]
    if target_key and target_key.tonic.name != "C":
        bass = transpose_pattern(bass, REF_KEY, target_key)
    return {
        "bass": bass,
        "figures": figures,
        "bars": 2,
        "cadence": "deceptive cadence",
    }


def cadence_plagal(target_key=None):
    """Plagal cadence: IV-I, 2 bars."""
    bass = ["F", "C"]
    figures = [["5", "3"], ["5", "3"]]
    if target_key and target_key.tonic.name != "C":
        bass = transpose_pattern(bass, REF_KEY, target_key)
    return {
        "bass": bass,
        "figures": figures,
        "bars": 2,
        "cadence": "plagal cadence",
    }


# ---------------------------------------------------------------------------
# Registry for lookup by name
# ---------------------------------------------------------------------------

SCHEMATA = {
    "romanesca": romanesca,
    "prinner": prinner,
    "monte": monte,
    "fonte": fonte,
    "rule_of_octave_ascending": rule_of_octave_ascending,
    "rule_of_octave_descending": rule_of_octave_descending,
    "cadence_authentic": cadence_authentic,
    "cadence_half": cadence_half,
    "cadence_deceptive": cadence_deceptive,
    "cadence_plagal": cadence_plagal,
}

# Non-cadential schemata used for building the body of a piece
BODY_SCHEMATA = ["romanesca", "prinner", "monte", "fonte"]

# Cadential schemata for endings and midpoints
CADENCE_SCHEMATA = [
    "cadence_authentic",
    "cadence_half",
    "cadence_deceptive",
    "cadence_plagal",
]
