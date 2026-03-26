from .generate import generate_partimento as _generate_partimento
from .realize import realize_partimento_satb as _realize_partimento_satb
from .review import review_partimento as _review_partimento
from .review import review_realized_score as _review_realized_score


class AlgorithmicPartimentoEngine:
    """Rule-based partimento engine using music theory algorithms instead of LLM."""

    def generate_partimento(self, prompt: str) -> dict:
        return _generate_partimento(prompt)

    def realize_partimento_satb(self, json_data) -> dict:
        return _realize_partimento_satb(json_data)

    def review_partimento(self, json_path: str) -> str:
        return _review_partimento(json_path)

    def review_realized_score(self, json_path: str) -> str:
        return _review_realized_score(json_path)
