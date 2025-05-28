# ![CI](https://github.com/radcliffetech/yantra-gandharva/actions/workflows/ci.yaml/badge.svg)
# ![Black](https://img.shields.io/badge/code%20style-black-000000.svg)

# Yantra Gandharva (यन्त्रगन्धर्व)

> 1. The sacred mechanism of celestial music  
> 2. A system that generates divine music through structured symbolic logic

---

## 🎯 Overview

**Yantra Gandharva** is a modular system for generating, realizing, and rendering symbolic music using large language models and structured score logic.  
It supports Baroque figured bass and jazz lead sheets, producing outputs as clean MusicXML files ready for notation software like Dorico or MuseScore.

---

## 🛠 Installation

1. Clone the repo and navigate into it:
   ```bash
   git clone https://github.com/your-username/yantra-gandharva.git
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
   ```

4. Add your OpenAI key in a `.env` file:
   ```
   OPENAI_API_KEY=your-key-here
   ```

---

## 🚀 Usage

### 🎷 Generate a jazz lead sheet:
```bash
python cli/main.py llm-generate jazz "Create a jazz lead sheet in F major with a I-vi-ii-V progression"
```

### 🎼 Realize figured bass:
```bash
python cli/main.py realize-figured-bass "Realize a figured bass progression in D minor ending with a cadence"
```

### 💾 Convert JSON to MusicXML:
```bash
python cli/main.py figured-bass generated/json/figured_YYYY-MM-DD_HHMMSS.json
```

### 📄 Inspect a MusicXML file:
```bash
python cli/main.py inspect-musicxml path/to/file.musicxml
```

---

## 🗂 Directory Structure

```
yantra-gandharva/
├── src/
│   ├── cli/
│   │   ├── main.py              # Entry point for CLI
│   │   ├── commands/            # CLI argument registration per domain
│   │   └── handlers/            # CLI action handlers per domain
│   ├── genres/                  # Domain-specific music logic (e.g., partimento, jazz)
│   ├── lib/                     # Shared tools and analysis utils
│   │   ├── analysis/
│   │   └── utils/
├── data/examples/               # Sample inputs and outputs
├── generated/chains/           # Realization chains with metadata and files
├── public/                      # Static assets (e.g., logo)
├── tests/                       # Test suite
├── pyproject.toml               # Python project configuration
├── requirements.txt             # Python dependency list
└── README.md
```

---

## 🧠 Future Ideas

- SATB chorale harmonization
- AI stylistic review of musical outputs
- Improvisation or ornamentation suggestions

---

## ✨ License

MIT License – use freely and compose boldly.
