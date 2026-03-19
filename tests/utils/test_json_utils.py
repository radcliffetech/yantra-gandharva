import json
import os
import tempfile

from lib.utils.json_utils import apply_patch, load_json


# ------------------------------------------------------------------
# apply_patch
# ------------------------------------------------------------------


def test_apply_patch_updates_single_voice():
    data = {
        "soprano": [["C5"], ["D5"], ["E5"]],
        "alto": [["A3"], ["B3"], ["C4"]],
    }
    patch = {"soprano": {"1": ["F5"]}}
    result = apply_patch(data, patch)
    assert result["soprano"][1] == ["F5"]
    assert result["soprano"][0] == ["C5"]  # unchanged


def test_apply_patch_updates_multiple_voices():
    data = {
        "soprano": [["C5"], ["D5"]],
        "alto": [["A3"], ["B3"]],
        "tenor": [["G3"], ["F3"]],
        "bass": [["C2"], ["G2"]],
    }
    patch = {
        "soprano": {"0": ["E5"]},
        "alto": {"1": ["C4"]},
    }
    result = apply_patch(data, patch)
    assert result["soprano"][0] == ["E5"]
    assert result["alto"][1] == ["C4"]
    assert result["tenor"] == [["G3"], ["F3"]]  # unchanged


def test_apply_patch_ignores_unknown_parts():
    data = {"soprano": [["C5"]]}
    patch = {"flute": {"0": ["D5"]}}
    result = apply_patch(data, patch)
    assert result["soprano"] == [["C5"]]
    assert "flute" not in result


def test_apply_patch_ignores_out_of_bounds():
    data = {"soprano": [["C5"], ["D5"]]}
    patch = {"soprano": {"99": ["F5"]}}
    result = apply_patch(data, patch)
    assert result["soprano"] == [["C5"], ["D5"]]


def test_apply_patch_ignores_non_numeric_index():
    data = {"soprano": [["C5"]]}
    patch = {"soprano": {"abc": ["D5"]}}
    result = apply_patch(data, patch)
    assert result["soprano"] == [["C5"]]


# ------------------------------------------------------------------
# load_json
# ------------------------------------------------------------------


def test_load_json_reads_valid_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"key": "value"}, f)
        f.flush()
        result = load_json(f.name)
    os.unlink(f.name)
    assert result == {"key": "value"}


def test_load_json_returns_default_for_missing_file():
    result = load_json("/nonexistent/file.json", default={"fallback": True})
    assert result == {"fallback": True}


def test_load_json_returns_empty_dict_for_missing_file_no_default():
    result = load_json("/nonexistent/file.json")
    assert result == {}


def test_load_json_returns_default_for_invalid_json():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("not valid json {{")
        f.flush()
        result = load_json(f.name, default={"error": True})
    os.unlink(f.name)
    assert result == {"error": True}
