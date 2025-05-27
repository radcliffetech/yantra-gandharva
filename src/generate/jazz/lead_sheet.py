import json

from music21 import harmony, key, metadata, meter, note, stream


def create_lead_sheet(json_path: str, output_path: str):
    with open(json_path, "r") as f:
        data = json.load(f)

    score = stream.Score()
    score.metadata = metadata.Metadata()
    score.metadata.title = data.get("title", "Untitled")

    part = stream.Part()
    part.append(key.Key(data["key"]))
    part.append(meter.TimeSignature(data.get("meter", "4/4")))

    for i, pitch in enumerate(data["melody"]):
        m = stream.Measure(number=i + 1)

        n = note.Note(pitch)
        n.quarterLength = 4.0

        chord_symbol = data["chords"][i]
        h = harmony.ChordSymbol(chord_symbol)

        m.append(h)
        m.append(n)
        part.append(m)

    score.append(part)
    score.write("musicxml", fp=output_path)
