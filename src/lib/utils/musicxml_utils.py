from music21 import converter, metadata, note, stream


def _normalize_note(note_str: str) -> str:
    return (
        note_str.replace("♭", "b")
        .replace("♯", "#")
        .replace("𝄪", "##")
        .replace("𝄫", "bb")
    )


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
    print("Title:", meta["title"] or "Unknown")
    print("Composer:", meta["composer"] or "Unknown")
    print("Parts:", meta["parts"])
    print("Measures:", meta["measures"])

    if score.parts:
        first_part = score.parts[0]
        first_measure = first_part.measure(1)

        key_signature = first_measure.getContextByClass("KeySignature")
        if key_signature:
            print("Key Signature:", key_signature.sharps)
        else:
            print("Key Signature: not found")

        time_signature = first_measure.getContextByClass("TimeSignature")
        if time_signature:
            print("Time Signature:", time_signature.ratioString)
        else:
            print("Time Signature: not found")

        instruments = first_part.getInstruments(returnDefault=True)
        if instruments:
            names = [
                instr.partName or instr.instrumentName or "Unnamed"
                for instr in instruments
            ]
            print("Instruments:", ", ".join(names))
        else:
            print("Instruments: not specified")

    if meta["measures"] == 0:
        print("⚠️  Warning: no measures found.")
    if meta["parts"] == 0:
        print("⚠️  Warning: no parts found.")


def json_to_musicxml(json_data: dict):
    """
    Convert a JSON SATB realization (or wrapped {"data": …}) to a music21 Score.

    Expected payload keys: 'soprano', 'alto', 'tenor', 'bass', optionally 'title'.
    """
    # unwrap if necessary
    payload = json_data.get("data", json_data)

    # Basic score
    score = stream.Score()
    md = metadata.Metadata()
    md.title = payload.get("title", "Realized Partimento")
    score.insert(0, md)

    part_order = [
        ("soprano", "Soprano"),
        ("alto", "Alto"),
        ("tenor", "Tenor"),
        ("bass", "Bass"),
    ]

    for voice_key, part_name in part_order:
        if voice_key not in payload:
            continue
        part_stream = stream.Part(id=voice_key)
        part_stream.partName = part_name
        voice_measures = payload[voice_key]

        for m_idx, measure_notes in enumerate(voice_measures, start=1):
            meas = stream.Measure(number=m_idx)
            ql = 4.0 / max(len(measure_notes), 1)  # simple equal division
            for n_str in measure_notes:
                meas.append(note.Note(_normalize_note(n_str), quarterLength=ql))
            part_stream.append(meas)
        score.append(part_stream)

    return score
