import os
import tempfile

from music21 import instrument, key, metadata, meter, note, stream

from lib.utils import musicxml_utils


def make_sample_score():
    score = stream.Score()
    score.metadata = metadata.Metadata()
    score.metadata.title = "Test Title"
    score.metadata.composer = "Composer Name"

    part = stream.Part()
    for i in range(4):
        m = stream.Measure(number=i + 1)
        m.append(note.Note("C4", quarterLength=4.0))
        part.append(m)

    score.append(part)
    return score


def test_save_and_load_musicxml():
    score = make_sample_score()
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.musicxml")
        musicxml_utils.save_musicxml(score, path)
        assert os.path.exists(path)

        loaded = musicxml_utils.load_musicxml(path)
        assert isinstance(loaded, stream.Score)
        assert len(loaded.parts) == 1


def test_get_metadata():
    score = make_sample_score()
    meta = musicxml_utils.get_metadata(score)
    assert meta["title"] == "Test Title"
    assert meta["composer"] == "Composer Name"
    assert meta["parts"] == 1
    assert meta["measures"] == 4


def test_is_four_part_true():
    score = make_sample_score()
    assert musicxml_utils.is_four_part(score)


def test_print_score_summary(capsys):
    score = make_sample_score()
    musicxml_utils.print_score_summary(score)
    out = capsys.readouterr().out
    assert "Title: Test Title" in out
    assert "Composer: Composer Name" in out
    assert "Parts: 1" in out
    assert "Measures: 4" in out


def test_print_score_summary_extended(capsys):
    score = make_sample_score()

    # Add key and time signatures and instrument
    score.parts[0].insert(0, key.KeySignature(0))  # C Major
    score.parts[0].insert(0, meter.TimeSignature("4/4"))
    inst = instrument.Instrument()
    inst.partName = "Piano"
    inst.instrumentName = "Piano"
    score.parts[0].insert(0, inst)
    score.parts[0].partName = "Piano"

    musicxml_utils.print_score_summary(score)
    out = capsys.readouterr().out

    assert "Key Signature:" in out
    assert "Time Signature:" in out
    assert "Instruments: Piano" in out


def test_summary_on_real_musicxml_file(capsys):
    path = "data/examples/example_output.musicxml"
    score = musicxml_utils.load_musicxml(path)
    musicxml_utils.print_score_summary(score)
    out = capsys.readouterr().out
    assert "Title:" in out
    assert "Parts:" in out
    assert "Measures:" in out
