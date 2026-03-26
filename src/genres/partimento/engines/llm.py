from genres.partimento.tasks.generate import generate_partimento
from genres.partimento.tasks.realize import realize_partimento_satb
from genres.partimento.tasks.review import review_partimento, review_realized_score


class LLMPartimentoEngine:
    """Engine that delegates to existing LLM-based task functions."""

    def __init__(self, call_llm):
        self._call_llm = call_llm

    def generate_partimento(self, prompt: str) -> dict:
        return generate_partimento(prompt, self._call_llm)

    def realize_partimento_satb(self, json_data) -> dict:
        return realize_partimento_satb(json_data, self._call_llm)

    def review_partimento(self, json_path: str) -> str:
        return review_partimento(json_path, self._call_llm)

    def review_realized_score(self, json_path: str) -> str:
        return review_realized_score(json_path, self._call_llm)
