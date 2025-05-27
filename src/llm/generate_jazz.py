import json

from dotenv import load_dotenv

load_dotenv()

JAZZ_LEAD_SHEET_SYSTEM_PROMPT = """You are a jazz composer and arranger. 

Given a natural language prompt, generate a simple jazz lead sheet in JSON format with a melody and chord symbols."""

JAZZ_LEAD_SHEET_USER_PROMPT_TEMPLATE = """Prompt: Create a jazz lead sheet in F major with a blues progression.

Output JSON format:
{
  "title": "F Blues",
  "key": "F",
  "meter": "4/4",
  "melody": ["F4", "A4", "C5", "D5", "C5", "A4", "F4", "E4"],
  "chords": ["F7", "Bb7", "F7", "F7", "Bb7", "Bdim7", "F7", "C7"]
}
"""


def generate_jazz_lead_sheet(prompt: str, call_llm) -> dict:
    system_prompt = JAZZ_LEAD_SHEET_SYSTEM_PROMPT
    user_prompt = JAZZ_LEAD_SHEET_USER_PROMPT_TEMPLATE.replace(
        "Create a jazz lead sheet in F major with a blues progression", prompt
    )
    response = call_llm(system_prompt, user_prompt)
    return json.loads(response)
