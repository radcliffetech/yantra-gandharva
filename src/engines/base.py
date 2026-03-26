from typing import Protocol


class PartimentoEngine(Protocol):
    """Protocol defining the interface for partimento engines."""

    def generate_partimento(self, prompt: str) -> dict: ...

    def realize_partimento_satb(self, json_data) -> dict: ...

    def review_partimento(self, json_path: str) -> str: ...

    def review_realized_score(self, json_path: str) -> str: ...


class JazzEngine(Protocol):
    """Protocol defining the interface for jazz engines."""

    def generate_jazz_lead_sheet(self, prompt: str) -> dict: ...
