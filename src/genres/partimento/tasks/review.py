import json

from genres.partimento import prompts


def review_realized_score(json_path: str, call_llm) -> str:
    with open(json_path, "r") as f:
        data = json.load(f)["data"]

    flat_repr = json.dumps(data, indent=2)
    user_prompt = prompts.REVIEW_SATB_USER_PROMPT_TEMPLATE.replace(
        "{{realization}}", flat_repr
    )
    return call_llm(prompts.REVIEW_SATB_SYSTEM_PROMPT, user_prompt)


def review_partimento(json_path: str, call_llm) -> str:
    with open(json_path, "r") as f:
        data = json.load(f)["data"]

    flat_repr = json.dumps(data, indent=2)
    user_prompt = prompts.REVIEW_PARTIMENTO_USER_PROMPT_TEMPLATE.replace(
        "{{partimento}}", flat_repr
    )
    return call_llm(prompts.REVIEW_PARTIMENTO_SYSTEM_PROMPT, user_prompt)
