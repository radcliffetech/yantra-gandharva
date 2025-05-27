import os
import tempfile

from music21 import metadata, note, stream

from src.utils import musicxml_tools


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
        musicxml_tools.save_musicxml(score, path)
        assert os.path.exists(path)

        loaded = musicxml_tools.load_musicxml(path)
        assert isinstance(loaded, stream.Score)
        assert len(loaded.parts) == 1


def test_get_metadata():
    score = make_sample_score()
    meta = musicxml_tools.get_metadata(score)
    assert meta["title"] == "Test Title"
    assert meta["composer"] == "Composer Name"
    assert meta["parts"] == 1
    assert meta["measures"] == 4


def test_is_four_part_true():
    score = make_sample_score()
    assert musicxml_tools.is_four_part(score)


def test_print_score_summary(capsys):
    score = make_sample_score()
    musicxml_tools.print_score_summary(score)
    out = capsys.readouterr().out
    assert "Title: Test Title" in out
    assert "Composer: Composer Name" in out
    assert "Parts: 1" in out
    assert "Measures: 4" in out
