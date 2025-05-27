FIGURED_BASS_SYSTEM_PROMPT = """You are a Baroque music theorist and continuo specialist. 

Given a bassline and a series of figures, you will generate a four-voice SATB realization in a style appropriate to Claudio Furno's figured bass exercises."""

FIGURED_BASS_USER_PROMPT_TEMPLATE = """Realize this figured bass exercise into four voices in C major. 

Output JSON format:
{
  "key": "C",
  "bassline": ["C2", "D2", "G2", "C2"],
  "figures": [["6"], ["5"], ["6"], ["5"]],
  "realization": {
    "soprano": ["E5", "F5", "G5", "E5"],
    "alto": ["C4", "D4", "D4", "C4"],
    "tenor": ["G3", "A3", "B3", "G3"]
  }
}
"""
