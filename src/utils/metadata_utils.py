import uuid
from datetime import datetime


def generate_metadata(prompt: str, mode: str, system_prompt: str = None) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "mode": mode,
        "source": "prompt",
        "user_prompt": prompt,
        "system_prompt": system_prompt,
        "version": "0.1.0",
    }
