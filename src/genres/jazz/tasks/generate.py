import json

from ..prompts import JAZZ_LEAD_SHEET_SYSTEM_PROMPT, get_lead_sheet_system_prompt


def generate_jazz_lead_sheet(prompt: str, call_llm) -> dict:
    system_prompt = JAZZ_LEAD_SHEET_SYSTEM_PROMPT
    user_prompt = get_lead_sheet_system_prompt(prompt)
    response = call_llm(system_prompt, user_prompt)
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON for jazz lead sheet: {e}")
