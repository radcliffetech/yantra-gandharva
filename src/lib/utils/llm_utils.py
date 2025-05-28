import os

import openai


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Call OpenAI Chat API and return JSON
    """
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
    return data
