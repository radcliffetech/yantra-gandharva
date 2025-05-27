import json
import os
import tempfile

from generate.jazz.lead_sheet import create_lead_sheet


def test_create_lead_sheet_creates_musicxml_file():
    test_data = {
        "title": "Test Tune",
        "key": "C",
        "meter": "4/4",
        "melody": ["C4", "E4", "G4", "A4"],
        "chords": ["Cmaj7", "Fmaj7", "G7", "Cmaj7"],
    }

    with tempfile.TemporaryDirectory() as tempdir:
        json_path = os.path.join(tempdir, "test_input.json")
        xml_path = os.path.join(tempdir, "test_output.xml")

        with open(json_path, "w") as f:
            json.dump(test_data, f)

        create_lead_sheet(json_path, xml_path)

        assert os.path.exists(xml_path)
        assert os.path.getsize(xml_path) > 0
