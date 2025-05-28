import json

from music21 import clef, key, metadata, meter, note, stream


def export_partimento_to_musicxml(json_path: str, output_path: str):
    with open(json_path, "r") as f:
        data = json.load(f)["data"]

    score = stream.Score()
    score.metadata = metadata.Metadata()
    score.metadata.title = data.get("title", "Partimento")

    part = stream.Part()
    part.insert(0, clef.BassClef())
    key_str = data.get("key", "C")
    parts = key_str.split()
    tonic = parts[0]
    mode = parts[1] if len(parts) > 1 else "major"
    part.append(key.Key(tonic, mode))
    part.append(meter.TimeSignature("4/4"))

    bassline = data["bassline"]
    figures = data["figures"]

    # Normalize bassline if flat (e.g., ["C2", "D2", ...])
    if all(isinstance(note, str) for note in bassline):
        bassline = [[n] for n in bassline]

    for i, measure_notes in enumerate(bassline):
        m = stream.Measure(number=i + 1)
        note_count = len(measure_notes)
        ql = 4.0 / note_count if note_count > 0 else 4.0

        for j, bass_note_str in enumerate(measure_notes):
            note_str = normalize_note_string(bass_note_str)
            try:
                bass = note.Note(note_str)
                bass.quarterLength = ql

                fig = figures[i][j] if i < len(figures) and j < len(figures[i]) else []
                if fig:
                    txt = " ".join(fig)
                    bass.addLyric(txt)

                m.append(bass)
            except Exception as e:
                print(f"⚠️ Skipping invalid bass note '{bass_note_str}': {e}")

        part.append(m)

    score.append(part)
    score.write("musicxml", fp=output_path)


def export_realized_partimento_to_musicxml(realized_json_path: str, output_path: str):
    with open(realized_json_path, "r") as f:
        data = json.load(f)["data"]

    score = stream.Score()
    score.metadata = metadata.Metadata()
    score.metadata.title = data.get("title", "Realized Partimento")

    for voice_name in ["soprano", "alto", "tenor", "bass"]:
        voice_notes = data[voice_name]
        part = stream.Part(id=voice_name)
        part.partName = voice_name.capitalize()
        part.append(key.Key("C", "major"))  # Default key; ideally parsed separately
        part.append(meter.TimeSignature("4/4"))

        for i, measure_notes in enumerate(voice_notes):
            m = stream.Measure(number=i + 1)
            note_count = len(measure_notes)
            ql = 4.0 / note_count if note_count > 0 else 4.0

            for note_str in measure_notes:
                normalized = (
                    note_str.replace("♯", "#").replace("♭", "b").replace("♮", "")
                )
                try:
                    n = note.Note(normalized)
                    n.quarterLength = ql
                    m.append(n)
                except Exception as e:
                    print(f"⚠️  Skipped note '{note_str}': {e}")
                    continue

            part.append(m)

        score.append(part)

    score.write("musicxml", fp=output_path)


def export_realized_partimento_to_midi(realized_json_path: str, output_path: str):
    """
    Export a realized partimento SATB JSON file to a MIDI file.
    """
    with open(realized_json_path, "r") as f:
        data = json.load(f)["data"]

    score = stream.Score()
    score.metadata = metadata.Metadata()
    score.metadata.title = data.get("title", "Realized Partimento")

    for voice_name in ["soprano", "alto", "tenor", "bass"]:
        voice_notes = data[voice_name]
        part = stream.Part(id=voice_name)
        part.partName = voice_name.capitalize()

        for i, measure_notes in enumerate(voice_notes):
            m = stream.Measure(number=i + 1)
            note_count = len(measure_notes)
            ql = 4.0 / note_count if note_count > 0 else 4.0

            for note_str in measure_notes:
                normalized = (
                    note_str.replace("♯", "#").replace("♭", "b").replace("♮", "")
                )
                try:
                    n = note.Note(normalized)
                    n.quarterLength = ql
                    m.append(n)
                except Exception as e:
                    print(f"⚠️  Skipped note '{note_str}': {e}")
                    continue

            part.append(m)

        score.append(part)

    score.write("midi", fp=output_path)


def normalize_note_string(note_str: str) -> str:
    return (
        note_str.replace("♭", "b")
        .replace("♯", "#")
        .replace("𝄪", "##")
        .replace("𝄫", "bb")
    )


def export_partimento_to_midi(json_path: str, output_path: str):
    """
    Export a partimento JSON file to a MIDI file.
    """
    with open(json_path, "r") as f:
        data = json.load(f)["data"]

    score = stream.Score()
    score.metadata = metadata.Metadata()
    score.metadata.title = data.get("title", "Partimento")

    part = stream.Part()
    part.insert(0, clef.BassClef())
    key_str = data.get("key", "C")
    parts = key_str.split()
    tonic = parts[0]
    mode = parts[1] if len(parts) > 1 else "major"
    part.append(key.Key(tonic, mode))
    part.append(meter.TimeSignature("4/4"))

    bassline = data["bassline"]
    figures = data["figures"]

    if all(isinstance(note, str) for note in bassline):
        bassline = [[n] for n in bassline]

    for i, measure_notes in enumerate(bassline):
        m = stream.Measure(number=i + 1)
        note_count = len(measure_notes)
        ql = 4.0 / note_count if note_count > 0 else 4.0

        for j, bass_note_str in enumerate(measure_notes):
            bass = note.Note(normalize_note_string(bass_note_str))
            bass.quarterLength = ql

            fig = figures[i][j] if i < len(figures) and j < len(figures[i]) else []
            if fig:
                txt = " ".join(fig)
                bass.addLyric(txt)

            m.append(bass)

        part.append(m)

    score.append(part)
    score.write("midi", fp=output_path)
