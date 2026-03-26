from genres.jazz.tasks.generate import generate_jazz_lead_sheet


class LLMJazzEngine:
    """Engine that delegates to existing LLM-based jazz task functions."""

    def __init__(self, call_llm):
        self._call_llm = call_llm

    def generate_jazz_lead_sheet(self, prompt: str) -> dict:
        return generate_jazz_lead_sheet(prompt, self._call_llm)
