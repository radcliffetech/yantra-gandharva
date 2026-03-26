# ![CI](https://github.com/radcliffetech/yantra-gandharva/actions/workflows/ci.yaml/badge.svg)
# ![Black](https://img.shields.io/badge/code%20style-black-000000.svg)

# Yantra Gandharva

> 1. The sacred mechanism of celestial music
> 2. A system that generates divine music through structured symbolic logic

---

## Overview

**Yantra Gandharva** is a modular system for generating, realizing, and rendering symbolic music using structured score logic.
It supports Baroque figured bass (partimento) and jazz lead sheets, producing outputs as clean MusicXML files ready for notation software like Dorico or MuseScore.

Two execution modes are available:

- **LLM mode** (`--engine llm`, default) — uses OpenAI GPT-4o for creative, varied output. Requires an API key.
- **Algorithmic mode** (`--engine algorithmic`) — uses rule-based music theory (Galant schemata, music21's figured bass realizer, jazz templates). Fully offline, deterministic, and free.

---

## Installation

1. Clone the repo and navigate into it:
   ```bash
   git clone https://github.com/radcliffetech/yantra-gandharva.git
   cd yantra-gandharva
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. (Optional — only needed for LLM mode) Add your OpenAI key in a `.env` file:
   ```
   OPENAI_API_KEY=your-key-here
   ```

---

## Usage

### Full partimento chain (generate, review, realize, export):
```bash
# Using LLM (default):
yantra chain-realization "8 bars in C major, Furno style"

# Using algorithmic engine (no API key needed):
yantra chain-realization "8 bars in D minor, Romanesca then Prinner" --engine algorithmic
```

### Generate a partimento bassline:
```bash
yantra generate-partimento "Rule of the Octave in G major, 16 bars" --engine algorithmic
```

### Realize a partimento into SATB texture:
```bash
yantra realize-partimento generated/json/partimento.json --engine algorithmic
```

### Review a partimento or realization:
```bash
yantra review-partimento generated/chains/partimento_01.json --engine algorithmic
yantra review-realization generated/chains/realized_01.json --engine algorithmic
```

### Generate a jazz lead sheet:
```bash
yantra generate-lead-sheet "12-bar blues in F" --engine algorithmic
yantra generate-lead-sheet "rhythm changes in Bb" --engine algorithmic
```

### Export JSON to MusicXML:
```bash
yantra lead-sheet data/examples/lead_sheet_example.json
yantra export-partimento generated/json/partimento.json
yantra export-realization generated/json/realized.json
```

### Inspect a MusicXML file:
```bash
yantra inspect-musicxml path/to/file.musicxml
```

---

## Algorithmic Engine

The algorithmic engine uses rule-based music theory instead of an LLM:

**Partimento generation** assembles basslines from Galant schemata:
- Romanesca, Prinner, Monte, Fonte
- Rule of the Octave (ascending/descending)
- Cadential formulas (authentic, half, deceptive, plagal)

**SATB realization** uses music21's `figuredBass.realizer` for constraint-based voice leading — no parallel 5ths/8ves, proper spacing, voice ranges.

**Review** checks for: awkward leaps, missing cadences, voice crossing, spacing violations, parallel 5ths/8ves, doubled leading tones, range violations.

**Jazz generation** uses templates: 12-bar blues, minor blues, 32-bar rhythm changes (AABA), 16-bar standard, ii-V-I patterns — all transposable to any key.

---

## Directory Structure

```
yantra-gandharva/
├── src/
│   ├── cli/
│   │   ├── main.py              # Entry point for CLI
│   │   ├── commands/            # CLI argument registration per domain
│   │   └── handlers/            # CLI action handlers per domain
│   ├── engines/                 # Engine abstraction (LLM vs algorithmic)
│   ├── genres/                  # Domain-specific music logic
│   │   ├── partimento/
│   │   │   ├── engines/         # LLM and algorithmic partimento engines
│   │   │   └── tasks/           # Export, generation, realization, review
│   │   └── jazz/
│   │       ├── engines/         # LLM and algorithmic jazz engines
│   │       └── tasks/           # Export, generation
│   └── lib/                     # Shared tools and analysis utils
│       ├── analysis/            # Voice-leading linter
│       └── utils/               # LLM, MusicXML, chain, music utilities
├── data/examples/               # Sample inputs and outputs
├── docs/                        # Roadmap, how-to guides
├── tests/                       # Test suite (202 tests)
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## License

MIT License
