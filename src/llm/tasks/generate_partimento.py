"""
LLM-based generation of partimento bass lines in the Neapolitan tradition.
"""

import json

from dotenv import load_dotenv

from ..prompts.partimento import (
    PARTIMENTO_SYSTEM_PROMPT,
    PARTIMENTO_USER_PROMPT_TEMPLATE,
)

load_dotenv()


def generate_partimento(prompt: str, call_llm) -> dict:
    """
    Given a natural language prompt describing a partimento,
    use the provided LLM call function to generate a structured partimento bass line in JSON format.
    """
    system_prompt = PARTIMENTO_SYSTEM_PROMPT
    user_prompt = PARTIMENTO_USER_PROMPT_TEMPLATE.replace(
        "Generate an unfigured partimento", prompt
    )
    response = call_llm(system_prompt, user_prompt)
    return json.loads(response)
