import json

from src.llm import generate_score


def test_prompt_to_json_jazz(monkeypatch):
    # Fake LLM response
    fake_response = json.dumps(
        {
            "title": "Test Tune",
            "key": "C",
            "meter": "4/4",
            "melody": ["C4", "E4", "G4", "A4"],
            "chords": ["Cmaj7", "Fmaj7", "G7", "Cmaj7"],
        }
    )

    # Monkeypatch the call_llm function
    def mock_call_llm(system_prompt, user_prompt):
        return fake_response

    monkeypatch.setattr(generate_score, "call_llm", mock_call_llm)

    result = generate_score.prompt_to_json(
        "Create a simple jazz lead sheet in C major", "jazz"
    )
    assert result["title"] == "Test Tune"
    assert result["key"] == "C"
    assert result["chords"] == ["Cmaj7", "Fmaj7", "G7", "Cmaj7"]


def test_realize_figured_bass_from_prompt(monkeypatch):
    fake_response = json.dumps(
        {
            "key": "C",
            "bassline": ["C2", "D2", "G2", "C2"],
            "figures": [["6"], ["5"], ["6"], ["5"]],
            "realization": {
                "soprano": ["E5", "F5", "G5", "E5"],
                "alto": ["C4", "D4", "D4", "C4"],
                "tenor": ["G3", "A3", "B3", "G3"],
            },
        }
    )

    def mock_call_llm(system_prompt, user_prompt):
        return fake_response

    monkeypatch.setattr(generate_score, "call_llm", mock_call_llm)
    result = generate_score.prompt_to_json(
        "Create a simple jazz lead sheet in C major", "figured"
    )
    assert result["key"] == "C"
    assert result["bassline"] == ["C2", "D2", "G2", "C2"]
    assert result["realization"]["soprano"] == ["E5", "F5", "G5", "E5"]
