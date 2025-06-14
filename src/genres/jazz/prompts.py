JAZZ_LEAD_SHEET_SYSTEM_PROMPT = """You are a jazz composer and arranger. 

Given a natural language prompt, generate a simple jazz lead sheet in JSON format with a melody and chord symbols.
"""


def get_lead_sheet_system_prompt(prompt: str) -> str:

    return f"""Prompt: {prompt}

Output JSON format:
{
  "title": "F Blues",
  "key": "F",
  "meter": "4/4",
  "melody": ["F4", "A4", "C5", "D5", "C5", "A4", "F4", "E4"],
  "chords": ["F7", "Bb7", "F7", "F7", "Bb7", "Bdim7", "F7", "C7"]
}
"""
