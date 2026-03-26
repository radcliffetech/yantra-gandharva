from .generate import generate_jazz_lead_sheet as _generate_jazz_lead_sheet


class AlgorithmicJazzEngine:
    """Rule-based jazz engine using templates and music theory instead of LLM."""

    def generate_jazz_lead_sheet(self, prompt: str) -> dict:
        return _generate_jazz_lead_sheet(prompt)
