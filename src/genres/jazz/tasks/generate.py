import json

from ..prompts import JAZZ_LEAD_SHEET_SYSTEM_PROMPT, get_lead_sheet_system_prompt


def generate_jazz_lead_sheet(prompt: str, call_llm) -> dict:
    system_prompt = JAZZ_LEAD_SHEET_SYSTEM_PROMPT
    user_prompt = get_lead_sheet_system_prompt(
        "Create a jazz lead sheet in F major with a blues progression", prompt
    )
    response = call_llm(system_prompt, user_prompt)
    return json.loads(response)
