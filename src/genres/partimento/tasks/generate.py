import json

from dotenv import load_dotenv

from ..prompts import PARTIMENTO_SYSTEM_PROMPT, get_partimento_user_prompt

load_dotenv()


# ---------------------------------------------------------------------------
# Pre‑built style cards.  Call code can inject one of these by serialising it
# to JSON and appending it to the system prompt with the prefix "STYLE_CARD: ".
# ---------------------------------------------------------------------------
STYLE_CARDS = {
    "Furno": {
        "name": "Francesco Furno",
        "era": "Neapolitan school, early 18th c.",
        "bass_texture": "pedagogical clarity, mostly stepwise motion with didactic sequences",
        "cadence_pref": "half and authentic cadences, clearly marked with 5‑1 bass motion",
        "chromaticism": "minimal; diatonic with the occasional raised leading tone",
    },
    "Palestrina": {
        "name": "Giovanni Pierluigi da Palestrina",
        "era": "Late Renaissance (modal counterpoint)",
        "bass_texture": "smooth modal lines, predominantly stepwise, frequent 4th/5th outlines",
        "cadence_pref": "modal clausulae, often Landini‑type upper‑voice cadences",
        "chromaticism": "very sparse; musica ficta limited to cadential leading tones",
    },
    "J. S. Bach": {
        "name": "Johann Sebastian Bach",
        "era": "High Baroque",
        "bass_texture": "robust circle‑of‑fifths progressions, sequential pedal points, chromatic bass lines",
        "cadence_pref": "strong PACs with 6‑4 → 5‑3 cadential pattern; occasional Phrygian half in minor",
        "chromaticism": "rich; uses secondary dominants, chromatic passing tones, and Neapolitan II",
    },
    "C. P. E. Bach": {
        "name": "Carl Philipp Emanuel Bach",
        "era": "Empfindsamer Stil (mid‑18th c.)",
        "bass_texture": "lively, many passing figures, sudden rests and expressive sigh motifs",
        "cadence_pref": "strong PACs with accented 6‑4 → 5‑3, frequent deceptive cadences for surprise",
        "chromaticism": "frequent raised leading tones in minor, expressive Neapolitan II and augmented‑sixth sonorities",
    },
}


def generate_partimento(prompt: str, call_llm) -> dict:
    """
    Given a natural language prompt describing a partimento,
    use the provided LLM call function to generate a structured partimento bass line in JSON format.
    """
    system_prompt = PARTIMENTO_SYSTEM_PROMPT
    user_prompt = get_partimento_user_prompt(
        prompt, style_card=STYLE_CARDS["J. S. Bach"]
    )
    response = call_llm(system_prompt, user_prompt)
    return json.loads(response)
