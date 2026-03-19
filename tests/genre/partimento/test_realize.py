import json

import pytest

from genres.partimento.tasks.realize import realize_partimento_satb


VALID_REALIZATION_JSON = json.dumps(
    {
        "soprano": [["E5"], ["D5"], ["C5"], ["D5"]],
        "alto": [["C4"], ["B3"], ["A3"], ["B3"]],
        "tenor": [["G3"], ["F3"], ["E3"], ["F3"]],
        "bass": [["C2"], ["G2"], ["A2"], ["G2"]],
    }
)

SAMPLE_INPUT = {
    "title": "Partimento in C",
    "key": "C major",
    "bassline": [["C2"], ["G2"], ["A2"], ["G2"]],
    "figures": [[[]], [[]], [[]], [[]]],
}


def test_realize_returns_four_voices():
    def mock_llm(system_prompt, user_prompt):
        return VALID_REALIZATION_JSON

    result = realize_partimento_satb(SAMPLE_INPUT, mock_llm)
    assert isinstance(result, dict)
    assert "soprano" in result
    assert "alto" in result
    assert "tenor" in result
    assert "bass" in result


def test_realize_passes_input_to_llm():
    captured = {}

    def mock_llm(system_prompt, user_prompt):
        captured["user"] = user_prompt
        return VALID_REALIZATION_JSON

    realize_partimento_satb(SAMPLE_INPUT, mock_llm)
    assert "C2" in captured["user"]
    assert "Realize this object" in captured["user"]


def test_realize_invalid_json_raises():
    def mock_llm(system_prompt, user_prompt):
        return "{{invalid"

    with pytest.raises(ValueError, match="LLM returned invalid JSON"):
        realize_partimento_satb(SAMPLE_INPUT, mock_llm)


def test_realize_voice_lengths_match():
    def mock_llm(system_prompt, user_prompt):
        return VALID_REALIZATION_JSON

    result = realize_partimento_satb(SAMPLE_INPUT, mock_llm)
    lengths = {len(result[v]) for v in ("soprano", "alto", "tenor", "bass")}
    assert len(lengths) == 1, "All voices should have the same number of measures"
