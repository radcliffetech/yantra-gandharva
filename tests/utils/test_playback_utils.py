import os
import tempfile

from lib.utils.playback_utils import open_file_if_possible


def test_open_file_if_possible_returns_none_for_missing_file():
    result = open_file_if_possible("/nonexistent/path/file.ogg")
    assert result is None


def test_open_file_if_possible_does_not_raise_for_existing_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test")
        path = f.name
    try:
        # Should not raise even if the file can't be opened by system player
        open_file_if_possible(path)
    finally:
        os.unlink(path)
