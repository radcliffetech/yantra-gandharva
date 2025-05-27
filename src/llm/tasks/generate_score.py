from .generate_jazz import generate_jazz_lead_sheet
from .realize_figured_bass import generate_figured_bass_realization


def prompt_to_json(prompt: str, score_type: str, call_llm) -> dict:
    """
    Convert natural language prompt into structured JSON score data
    for 'figured' or 'jazz'.
    """
    if score_type == "figured":
        return generate_figured_bass_realization(prompt, call_llm)
    elif score_type == "jazz":
        return generate_jazz_lead_sheet(prompt, call_llm)
    else:
        raise ValueError(f"Unsupported score type: {score_type}")
