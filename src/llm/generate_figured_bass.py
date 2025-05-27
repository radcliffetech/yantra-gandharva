"""
LLM-based realization of figured bass exercises into four-part SATB texture.
"""

import json
import os

import openai
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


FIGURED_BASS_SYSTEM_PROMPT = """You are a Baroque music theorist and continuo specialist. 

Given a bassline and a series of figures, you will generate a four-voice SATB realization in a style appropriate to Claudio Furno's figured bass exercises."""

FIGURED_BASS_USER_PROMPT_TEMPLATE = """Realize this figured bass exercise into four voices in C major. 

Output JSON format:
{
  "key": "C",
  "bassline": ["C2", "D2", "G2", "C2"],
  "figures": [["6"], ["5"], ["6"], ["5"]],
  "realization": {
    "soprano": ["E5", "F5", "G5", "E5"],
    "alto": ["C4", "D4", "D4", "C4"],
    "tenor": ["G3", "A3", "B3", "G3"]
  }
}
"""


def generate_figured_bass_realization(prompt: str, call_llm) -> dict:
    """
    Given a natural language prompt describing a figured bass progression,
    use the provided LLM call function to generate a realized four-part texture in JSON format.
    """
    system_prompt = FIGURED_BASS_SYSTEM_PROMPT
    user_prompt = FIGURED_BASS_USER_PROMPT_TEMPLATE.replace(
        "Realize this figured bass exercise", prompt
    )
    response = call_llm(system_prompt, user_prompt)
    return json.loads(response)
