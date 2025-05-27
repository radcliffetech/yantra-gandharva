PARTIMENTO_SYSTEM_PROMPT = """You are an 18th-century composition teacher trained in the Neapolitan partimento tradition.

Given a key, number of measures, and stylistic goals, generate an unfigured or optionally figured partimento bass line suitable for student realization. Each measure may contain one or more bass notes. Use nested arrays to group notes by measure. Do not include a realization. Output structured JSON."""

PARTIMENTO_USER_PROMPT_TEMPLATE = """Generate an unfigured partimento in C major, 4 measures long, with cadences in measures 2 and 4.

Output JSON format:
{
  "title": "Partimento in C",
  "key": "C major",
  "bassline": [
    ["C2", "D2"],
    ["E2"],
    ["F2", "E2", "D2"],
    ["G2"]
  ],
  "figures": [
    [[], ["6"]],
    [[]],
    [["6"], [], ["5"]],
    [["5", "3"]]
  ],
  "cadences": ["measure 2: half cadence", "measure 4: authentic cadence"],
  "style": "Furno (Neapolitan school)",
  "modulations": []
}
"""
