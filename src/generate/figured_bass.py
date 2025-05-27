import json

from music21 import chord, key, metadata, meter, note, stream


def create_figured_bass_realization(json_path: str, output_path: str):
    with open(json_path, "r") as f:
        data = json.load(f)

    if "realization" not in data:
        raise ValueError(
            "The input JSON is missing a 'realization' key. Please run the LLM generation step first to create a four-part realization."
        )

    score = stream.Score()
    score.metadata = metadata.Metadata()
    score.metadata.title = data.get("title", "Figured Bass Realization")

    part = stream.Part()
    part.append(key.Key(data["key"]))
    part.append(meter.TimeSignature("4/4"))

    bassline = data["bassline"]
    figures = data["figures"]
    realization = data["realization"]

    for i, bass_note_str in enumerate(bassline):
        m = stream.Measure(number=i + 1)

        bass = note.Note(bass_note_str)
        bass.quarterLength = 4.0

        tenor = note.Note(realization["tenor"][i])
        tenor.quarterLength = 4.0

        alto = note.Note(realization["alto"][i])
        alto.quarterLength = 4.0

        soprano = note.Note(realization["soprano"][i])
        soprano.quarterLength = 4.0

        m.append(bass)
        m.append(tenor)
        m.append(alto)
        m.append(soprano)
        part.append(m)

    score.append(part)
    score.write("musicxml", fp=output_path)
