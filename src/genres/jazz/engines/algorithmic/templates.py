"""
Jazz lead sheet templates — common chord progressions and forms.

Each template returns chords in a reference key. Transposition is
handled by the caller. Melody is generated separately based on chord tones.
"""

from music21 import harmony, interval, key, pitch


# ---------------------------------------------------------------------------
# Transposition
# ---------------------------------------------------------------------------


def transpose_chords(chords, from_key_str, to_key_str):
    """Transpose a list of chord symbol strings from one key to another.

    Uses music21's harmony.ChordSymbol for correct enharmonic handling.
    """
    from_tonic = pitch.Pitch(from_key_str)
    to_tonic = pitch.Pitch(to_key_str)
    trans = interval.Interval(noteStart=from_tonic, noteEnd=to_tonic)

    result = []
    for chord_str in chords:
        cs = harmony.ChordSymbol(chord_str)
        cs = cs.transpose(trans)
        result.append(cs.figure)
    return result


def transpose_melody(melody, from_key_str, to_key_str):
    """Transpose a list of pitch strings from one key to another.

    Uses the nearest transposition interval (up or down) to keep
    the melody in a similar octave range as the original.
    """
    from_tonic = pitch.Pitch(from_key_str + "4")
    to_tonic = pitch.Pitch(to_key_str + "4")

    # Choose the smaller of the two possible intervals (up vs down)
    trans_up = interval.Interval(noteStart=from_tonic, noteEnd=to_tonic)
    if abs(trans_up.semitones) > 6:
        # Use the complementary interval in the other direction
        if trans_up.semitones > 0:
            to_tonic_low = pitch.Pitch(to_key_str + "3")
            trans = interval.Interval(noteStart=from_tonic, noteEnd=to_tonic_low)
        else:
            to_tonic_high = pitch.Pitch(to_key_str + "5")
            trans = interval.Interval(noteStart=from_tonic, noteEnd=to_tonic_high)
    else:
        trans = trans_up

    result = []
    for note_str in melody:
        p = pitch.Pitch(note_str)
        p = p.transpose(trans)
        result.append(str(p))
    return result


# ---------------------------------------------------------------------------
# Templates (all in C major reference key)
# ---------------------------------------------------------------------------


def blues_12bar():
    """12-bar blues in C.

    The foundational jazz form: I7-IV7-I7-V7 with standard changes.
    """
    chords = [
        "C7", "C7", "C7", "C7",
        "F7", "F7", "C7", "C7",
        "G7", "F7", "C7", "G7",
    ]
    melody = [
        "E4", "G4", "C5", "E5",
        "F4", "A4", "E4", "G4",
        "B4", "A4", "G4", "G4",
    ]
    return {
        "chords": chords,
        "melody": melody,
        "bars": 12,
        "form": "blues",
        "ref_key": "C",
    }


def blues_minor_12bar():
    """12-bar minor blues in C minor.

    Minor blues with bIII, bVI, bVII substitutions.
    """
    chords = [
        "Cm7", "Cm7", "Cm7", "Cm7",
        "Fm7", "Fm7", "Cm7", "Cm7",
        "A-maj7", "G7", "Cm7", "G7",
    ]
    melody = [
        "E-4", "G4", "C5", "E-5",
        "F4", "A-4", "E-4", "G4",
        "A-4", "B4", "G4", "G4",
    ]
    return {
        "chords": chords,
        "melody": melody,
        "bars": 12,
        "form": "minor blues",
        "ref_key": "C",
    }


def rhythm_changes_32bar():
    """32-bar AABA rhythm changes in C (based on 'I Got Rhythm').

    The second most common jazz form after blues.
    """
    # A section (8 bars)
    a_chords = ["Cmaj7", "Am7", "Dm7", "G7", "Cmaj7", "Am7", "Dm7", "G7"]
    a_melody = ["E5", "C5", "D5", "B4", "C5", "A4", "D5", "G4"]

    # B section (bridge, 8 bars)
    b_chords = ["E7", "E7", "A7", "A7", "D7", "D7", "G7", "G7"]
    b_melody = ["G#4", "B4", "C#5", "E5", "F#4", "A4", "B4", "D5"]

    chords = a_chords + a_chords + b_chords + a_chords  # AABA
    melody = a_melody + a_melody + b_melody + a_melody
    return {
        "chords": chords,
        "melody": melody,
        "bars": 32,
        "form": "AABA",
        "ref_key": "C",
    }


def standard_16bar():
    """16-bar jazz standard form in C.

    A common shorter form: two 8-bar sections.
    """
    chords = [
        # A section
        "Cmaj7", "Am7", "Dm7", "G7",
        "Em7", "A7", "Dm7", "G7",
        # B section
        "Cmaj7", "Fmaj7", "Bm7b5", "E7",
        "Am7", "D7", "Dm7", "G7",
    ]
    melody = [
        "E5", "C5", "F5", "D5",
        "E5", "C#5", "D5", "B4",
        "C5", "A4", "B4", "G#4",
        "A4", "F#4", "D5", "B4",
    ]
    return {
        "chords": chords,
        "melody": melody,
        "bars": 16,
        "form": "AB",
        "ref_key": "C",
    }


def ii_v_i_turnaround():
    """4-bar ii-V-I turnaround in C.

    The fundamental jazz cadential pattern.
    """
    chords = ["Dm7", "G7", "Cmaj7", "Cmaj7"]
    melody = ["F4", "B4", "E5", "C5"]
    return {
        "chords": chords,
        "melody": melody,
        "bars": 4,
        "form": "turnaround",
        "ref_key": "C",
    }


def ii_v_i_extended_8bar():
    """8-bar extended ii-V-I with secondary dominants in C."""
    chords = ["Dm7", "G7", "Cmaj7", "A7", "Dm7", "G7", "Cmaj7", "Cmaj7"]
    melody = ["F4", "B4", "E5", "C#5", "D5", "B4", "C5", "E5"]
    return {
        "chords": chords,
        "melody": melody,
        "bars": 8,
        "form": "ii-V-I extended",
        "ref_key": "C",
    }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TEMPLATES = {
    "blues": blues_12bar,
    "minor_blues": blues_minor_12bar,
    "rhythm_changes": rhythm_changes_32bar,
    "standard_16": standard_16bar,
    "turnaround": ii_v_i_turnaround,
    "ii_v_i": ii_v_i_extended_8bar,
}
