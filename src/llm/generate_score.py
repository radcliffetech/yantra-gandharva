import os

import openai

from .generate_figured_bass import generate_figured_bass_realization
from .generate_jazz import generate_jazz_lead_sheet

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Call OpenAI Chat API and return JSON
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )
    data = response.choices[0].message.content.strip()
    print(f"LLM Response: {data}")  # Debugging output
    return data


def prompt_to_json(prompt: str, score_type: str) -> dict:
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
