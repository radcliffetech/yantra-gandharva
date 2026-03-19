import json

import pytest

from genres.jazz.tasks.generate import generate_jazz_lead_sheet


VALID_LEAD_SHEET_JSON = json.dumps(
    {
        "title": "Blues in F",
        "key": "F",
        "meter": "4/4",
        "melody": ["F4", "A4", "C5", "D5"],
        "chords": ["F7", "Bb7", "F7", "C7"],
    }
)


def test_generate_jazz_returns_dict():
    def mock_llm(system_prompt, user_prompt):
        return VALID_LEAD_SHEET_JSON

    result = generate_jazz_lead_sheet("Blues in F major", mock_llm)
    assert isinstance(result, dict)
    assert result["key"] == "F"
    assert result["title"] == "Blues in F"


def test_generate_jazz_passes_user_prompt():
    captured = {}

    def mock_llm(system_prompt, user_prompt):
        captured["user"] = user_prompt
        return VALID_LEAD_SHEET_JSON

    generate_jazz_lead_sheet("Bebop tune in Bb minor", mock_llm)
    assert "Bebop tune in Bb minor" in captured["user"]


def test_generate_jazz_invalid_json_raises():
    def mock_llm(system_prompt, user_prompt):
        return "not json"

    with pytest.raises(ValueError, match="LLM returned invalid JSON"):
        generate_jazz_lead_sheet("any prompt", mock_llm)


def test_generate_jazz_preserves_all_fields():
    def mock_llm(system_prompt, user_prompt):
        return VALID_LEAD_SHEET_JSON

    result = generate_jazz_lead_sheet("Blues", mock_llm)
    expected_fields = {"title", "key", "meter", "melody", "chords"}
    assert expected_fields.issubset(result.keys())
