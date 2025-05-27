import json

from music21 import key, metadata, meter, note, stream


def export_partimento_to_musicxml(json_path: str, output_path: str):
    with open(json_path, "r") as f:
        data = json.load(f)

    score = stream.Score()
    score.metadata = metadata.Metadata()
    score.metadata.title = data.get("title", "Partimento")

    part = stream.Part()
    tonic, mode = data["key"].split()
    part.append(key.Key(tonic, mode))
    part.append(meter.TimeSignature("4/4"))

    bassline = data["bassline"]
    figures = data["figures"]

    for i, measure_notes in enumerate(bassline):
        m = stream.Measure(number=i + 1)
        note_count = len(measure_notes)
        ql = 4.0 / note_count if note_count > 0 else 4.0

        for j, bass_note_str in enumerate(measure_notes):
            bass = note.Note(bass_note_str)
            bass.quarterLength = ql

            fig = figures[i][j] if i < len(figures) and j < len(figures[i]) else []
            if fig:
                txt = " ".join(fig)
                bass.addLyric(txt)

            m.append(bass)

        part.append(m)

    score.append(part)
    score.write("musicxml", fp=output_path)


def export_realized_partimento_to_musicxml(realized_json_path: str, output_path: str):
    with open(realized_json_path, "r") as f:
        data = json.load(f)

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
                n = note.Note(note_str)
                n.quarterLength = ql
                m.append(n)

            part.append(m)

        score.append(part)

    score.write("musicxml", fp=output_path)
