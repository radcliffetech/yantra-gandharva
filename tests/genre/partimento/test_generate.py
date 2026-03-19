import json

import pytest

from genres.partimento.tasks.generate import generate_partimento


VALID_PARTIMENTO_JSON = json.dumps(
    {
        "title": "Partimento in C",
        "key": "C major",
        "bassline": [["C2"], ["G2", "A2"], ["D2"], ["G2"]],
        "figures": [[[]], [["6"], []], [["6"]], [["5"]]],
        "cadences": ["measure 4: authentic cadence"],
        "style": "J. S. Bach (High Baroque)",
        "modulations": [],
    }
)


def test_generate_partimento_returns_dict():
    def mock_llm(system_prompt, user_prompt):
        return VALID_PARTIMENTO_JSON

    result = generate_partimento("C Major. 4 bars.", mock_llm)
    assert isinstance(result, dict)
    assert result["key"] == "C major"
    assert result["title"] == "Partimento in C"
    assert len(result["bassline"]) == 4


def test_generate_partimento_passes_prompt_to_llm():
    captured = {}

    def mock_llm(system_prompt, user_prompt):
        captured["system"] = system_prompt
        captured["user"] = user_prompt
        return VALID_PARTIMENTO_JSON

    generate_partimento("G minor. 8 bars. Fugal style.", mock_llm)
    assert "G minor. 8 bars. Fugal style." in captured["user"]
    assert "STYLE_CARD" in captured["user"]


def test_generate_partimento_invalid_json_raises():
    def mock_llm(system_prompt, user_prompt):
        return "not valid json {{"

    with pytest.raises(ValueError, match="LLM returned invalid JSON"):
        generate_partimento("C Major", mock_llm)


def test_generate_partimento_preserves_all_fields():
    def mock_llm(system_prompt, user_prompt):
        return VALID_PARTIMENTO_JSON

    result = generate_partimento("C Major", mock_llm)
    expected_fields = {"title", "key", "bassline", "figures", "cadences", "style", "modulations"}
    assert expected_fields.issubset(result.keys())
