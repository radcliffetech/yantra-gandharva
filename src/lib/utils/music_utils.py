from music21 import note, pitch

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
