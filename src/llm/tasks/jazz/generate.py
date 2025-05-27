import json

from dotenv import load_dotenv

from ...prompts.jazz import (
    JAZZ_LEAD_SHEET_SYSTEM_PROMPT,
    JAZZ_LEAD_SHEET_USER_PROMPT_TEMPLATE,
)

load_dotenv()


def generate_jazz_lead_sheet(prompt: str, call_llm) -> dict:
    system_prompt = JAZZ_LEAD_SHEET_SYSTEM_PROMPT
    user_prompt = JAZZ_LEAD_SHEET_USER_PROMPT_TEMPLATE.replace(
        "Create a jazz lead sheet in F major with a blues progression", prompt
    )
    response = call_llm(system_prompt, user_prompt)
    return json.loads(response)
