"""
LLM-based realization of figured bass exercises into four-part SATB texture.
"""

import json
import os

import openai
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from ..prompts.figured_bass import (
    FIGURED_BASS_SYSTEM_PROMPT,
    FIGURED_BASS_USER_PROMPT_TEMPLATE,
)


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
