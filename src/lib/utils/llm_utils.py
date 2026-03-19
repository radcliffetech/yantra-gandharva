import os

import openai

DEFAULT_MODEL = os.getenv("YANTRA_LLM_MODEL", "gpt-4o")


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Call OpenAI Chat API and return JSON
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set. "
            "Set it before running LLM commands."
        )
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )
    data = response.choices[0].message.content.strip()
    return data
