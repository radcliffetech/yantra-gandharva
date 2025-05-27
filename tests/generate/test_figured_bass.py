import json
import os
import tempfile

from src.generate.partimento import create_figured_bass_realization


def test_create_figured_bass_realization_creates_musicxml():
    test_data = {
        "title": "Test Figured Bass",
        "key": "C",
        "bassline": ["C2", "D2", "G2", "C2"],
        "figures": [["6"], ["5"], ["6"], ["5"]],
        "realization": {
            "soprano": ["E5", "F5", "G5", "E5"],
            "alto": ["C4", "D4", "D4", "C4"],
            "tenor": ["G3", "A3", "B3", "G3"],
        },
    }

    with tempfile.TemporaryDirectory() as tempdir:
        json_path = os.path.join(tempdir, "test_input.json")
        xml_path = os.path.join(tempdir, "test_output.musicxml")

        with open(json_path, "w") as f:
            json.dump(test_data, f)

        create_figured_bass_realization(json_path, xml_path)

        assert os.path.exists(xml_path)
        assert os.path.getsize(xml_path) > 0
