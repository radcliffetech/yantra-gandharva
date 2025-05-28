"""
LLM-based generation of partimento bass lines in the Neapolitan tradition.
"""

import json

from dotenv import load_dotenv

from ..prompts import PARTIMENTO_REALIZE_SATB_SYSTEM_PROMPT

load_dotenv()


def realize_partimento_satb(json_data: str, call_llm) -> dict:
    user_prompt = "Realize this object:\n\n" + json.dumps(json_data, indent=2)
    response = call_llm(PARTIMENTO_REALIZE_SATB_SYSTEM_PROMPT, user_prompt)
    return json.loads(response)
