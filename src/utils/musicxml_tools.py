from music21 import converter, note


def load_musicxml(path: str):
    """Load a MusicXML file into a music21 stream.Score."""
    return converter.parse(path)


def save_musicxml(score, path: str):
    """Save a music21 score to MusicXML."""
    score.write("musicxml", fp=path)


def get_metadata(score):
    """Extract basic metadata from a music21 score."""
    return {
        "title": score.metadata.title if score.metadata else None,
        "composer": score.metadata.composer if score.metadata else None,
        "parts": len(score.parts),
        "measures": (
            sum(1 for _ in score.parts[0].getElementsByClass("Measure"))
            if score.parts
            else 0
        ),
    }


def is_four_part(score):
    """Check if the score is a single-part SATB realization."""
    return len(score.parts) == 1 and all(
        isinstance(n, note.Note)
        for m in score.parts[0].getElementsByClass("Measure")
        for n in m.notes
    )


def print_score_summary(score):
    """Print a human-readable summary of a score."""
    meta = get_metadata(score)
    print("Title:", meta["title"])
    print("Composer:", meta["composer"])
    print("Parts:", meta["parts"])
    print("Measures:", meta["measures"])
