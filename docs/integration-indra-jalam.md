# Integrating Yantra Gandharva with Indra Jalam

> Design notes for connecting the symbolic music composition system (Yantra Gandharva) with the categorical simulation framework (Indra Jalam).

---

## Overview

These two projects approach music from opposite directions:

| | Yantra Gandharva | Indra Jalam |
|---|---|---|
| **Approach** | Score-first: generate symbolic music (JSON/MusicXML) | Simulation-first: agents evolve toward coherent music |
| **Language** | Python + music21 | Pure C + Gita formulas |
| **Music theory** | Figured bass, schemata, chord templates | Chord charts, voice leading, `chord_target()` |
| **Output** | MusicXML, MIDI, OGG (static files) | MIDI real-time via CoreMIDI, SVG, JSON |
| **Intelligence** | LLM or algorithmic rules | Geometric coherence (Drishti) + agent evolution |
| **Measurement** | `lint_satb()` rule-based checking | Drishti information-theoretic coherence scoring |

They share deep overlap in domain (Baroque voice leading, figured bass, SATB voicing) but have complementary strengths. The integration opportunities below are ordered from lowest-friction to highest-impact.

---

## Integration 1: Drishti as a Coherence Reviewer

**Effort:** Low (Python bindings already exist)

**Idea:** Use Drishti's coherence scoring as an alternative or complement to the rule-based review engine. Instead of checking "did you break any voice-leading rules?", ask "does this realization have structured coherence?"

**How it works:**
- Take a generated SATB realization's four voice lines
- Convert each voice to a normalized signal (MIDI pitch values / 127)
- Score each voice through `drishti_score()` via the `indriya` Python bindings
- Compose the per-voice pathways into an overall coherence metric
- A well-voiced realization should score above the 1/sqrt(2) threshold

**Why it's valuable:**
- Catches problems that rules miss (e.g. a realization that follows all rules but sounds aimless)
- Provides a single scalar quality metric instead of a checklist
- Mathematically grounded in information theory, not convention
- Complements rule-based review: rules catch specific violations, Drishti catches structural incoherence

**Implementation sketch:**
```python
# In genres/partimento/engines/algorithmic/review.py or a new module

from indriya.drishti import score as drishti_score

def coherence_review(realized_data: dict) -> float:
    """Score SATB realization coherence via Drishti."""
    pathways = []
    for voice in ["soprano", "alto", "tenor", "bass"]:
        flat = [note for measure in realized_data[voice] for note in measure]
        signal = [pitch_to_midi(n) / 127.0 for n in flat]
        score = drishti_score(signal)
        pathways.append(score.pathway)
    # Geometric mean of all voice pathways
    composed = (pathways[0] * pathways[1] * pathways[2] * pathways[3]) ** 0.25
    return composed
```

---

## Integration 2: Smriti as Score Memory

**Effort:** Low-medium (Python bindings exist, needs schema design)

**Idea:** Store every generated partimento and realization as a Smriti card (Vec9 geometric fingerprint + metadata). Query by similarity across sessions.

**What it enables:**
- "Find me realizations similar to this one"
- "What's the most coherent thing I've generated in D minor?"
- "Show me partimenti that used the Romanesca schema"
- Track quality over time as the algorithmic engine improves

**How it works:**
- After generating/realizing, score the output through Drishti to get a Vec9
- Store the Vec9 + metadata (key, style, schema, engine type, prompt) as a Smriti card
- The JSON output becomes the card's blob payload
- Query with `smriti_query_similar()` or `smriti_query_composable()` (threshold = 1/sqrt(2))

**Schema for a card:**

| Field | Source |
|-------|--------|
| `vec9` | Drishti score of the realization |
| `domain` | `"partimento"` or `"jazz"` |
| `key` | `"D minor"` |
| `style` | `"Furno"` |
| `engine` | `"algorithmic"` or `"llm"` |
| `prompt` | Original user prompt |
| `blob` | The full JSON output |

---

## Integration 3: Simha as a Generative Engine

**Effort:** Medium-high (needs spec generation + output parsing)

**Idea:** Add `--engine simha` as a third engine type. Define a Simha YAML spec from the partimento's harmonic plan, let agents evolve voice leading via coherence-driven simulation, then export the trajectory as SATB JSON.

**Why this is exciting:**
- Three fundamentally different paradigms behind one CLI:
  - **LLM:** creative, varied, opaque
  - **Algorithmic:** deterministic, transparent, rule-governed
  - **Simha:** emergent, coherence-driven, evolutionary
- Simha already has the infrastructure: chord charts with voice ranges, `chord_target()` builtin, figured bass notation, MIDI output
- The Chaconne spec (340 lines) demonstrates full Baroque composition in Simha

**Architecture:**

```
User prompt
  |
  v
Prompt parser extracts: key, bars, schemata, cadences
  |
  v
Spec generator builds YAML:
  - chord_chart from schemata (harmonic plan)
  - 4 agents (S, A, T, B) with voice ranges
  - integrate formulas using chord_target(voice_id)
  - coherence formula from voice-leading quality
  |
  v
simha run spec.yaml --output-json trajectory.json
  |
  v
Parse trajectory -> extract pitch sequences per voice -> SATB JSON
```

**Key challenge:** Building the spec generator. The prompt parser already extracts key, bars, and schemata. The schemata need to be translated into a chord chart (beat-by-beat chord symbols with durations). The voice agent formulas can follow the Chaconne pattern.

**Key advantage:** The simulation can _evolve_ its parameters until the trajectory scores above 1/sqrt(2). This means the output is guaranteed to be coherent by Drishti's measure — a property neither the LLM nor algorithmic engine can promise.

---

## Integration 4: Yantra Gandharva as a Spec Generator

**Effort:** Medium (builds on Integration 3)

**Idea:** Use Yantra Gandharva's music theory knowledge (schemata, prompt parsing, figured bass) to generate Simha specs. This turns natural language prompts into runnable simulations.

**Flow:**
```
"8 bars in D minor, Romanesca then Prinner, Bach style"
  |
  v
Yantra Gandharva generates:
  - Harmonic plan: Dm - C#dim - Bb - Am - Gm - F - E - Dm
  - Figures: 5/3, 6, 5/3, 6, 5/3, 6, 6/5, 5/3
  - Cadence at m8: authentic
  |
  v
Spec generator produces YAML:
  - chord_chart with 8 beats
  - 4 voice agents with ranges
  - Coherence = voice-leading smoothness
  |
  v
simha run → MIDI real-time to synthesizer
```

This makes Yantra Gandharva a creative front-end and Simha a performance engine.

---

## Integration 5: Live Performance Loop

**Effort:** High (needs real-time coordination)

**Idea:** Combine Simha's `serve` mode + MIDI real-time output + Yantra Gandharva's harmonic knowledge for live performance.

**Flow:**
```
Performer sends chord changes (SSE / stdin)
  |
  v
Simha serve mode receives chord input
  |
  v
Voice agents re-target via chord_target()
  |
  v
Agents evolve smooth voice leading in real time
  |
  v
CoreMIDI output to synthesizer / DAW
```

Yantra Gandharva's role: pre-compute harmonic progressions, figure sequences, and reharmonization options that feed into Simha as chord charts. The system becomes an AI accompanist.

---

## Recommended Starting Point

**Start with Integration 1 (Drishti as reviewer).**

It requires:
1. The `indriya` Python package installed in Yantra Gandharva's venv
2. A small module that converts SATB pitch sequences to normalized signals
3. A call to `drishti_score()` per voice
4. Composing the result into a single coherence metric

This gives immediate value (a quality metric grounded in information theory), validates the integration path, and creates the foundation for Integration 2 (Smriti storage, since you'll already be producing Vec9 fingerprints).

From there, Integration 3 (Simha engine) is the high-impact goal — it would make this the first composition system offering LLM, algorithmic, and agent-based generation behind a single interface.

---

## Technical Notes

### Python Bindings (indriya)

The `indriya` package wraps all four instruments via ctypes:

```python
from indriya.drishti import score_text, score_audio, DrishtiScore
from indriya.smriti import SmritiContext, SmritiCard
from indriya.simha import SimhaRunner
from indriya.gita import evaluate
```

This means Yantra Gandharva can call into Indra Jalam without compiling C or managing native libraries (beyond having `libindriya.dylib` available).

### Vec9 Layout

The 9-float geometric fingerprint that flows between all instruments:

| Index | Field | Meaning |
|-------|-------|---------|
| 0 | C | Fine-scale entropy |
| 1 | I | Fine-scale autocorrelation |
| 2 | pathway | sqrt(C * I) |
| 3 | C_coarse | Coarse-scale entropy |
| 4 | I_coarse | Coarse-scale autocorrelation |
| 5 | pathway_coarse | sqrt(C_coarse * I_coarse) |
| 6 | pathway_composed | sqrt(pathway * pathway_coarse) |
| 7 | coherent | 1.0 if pathway >= 1/sqrt(2) else 0.0 |
| 8 | level | pathway * 1000 (integer) |

### The Threshold

One number: **1/sqrt(2) = 0.7071067811865475**

This is not a tunable parameter. It's the Shannon channel boundary expressed as a geometric mean. A signal (or voice line, or simulation trajectory) either has enough structured coherence to cross it, or it doesn't.

### Chord Chart Compatibility

Simha's chord chart format maps closely to Yantra Gandharva's partimento JSON:

| Yantra Gandharva | Simha |
|---|---|
| `bassline[i]` | `chords[i].chord` (root) |
| `figures[i]` | `chords[i].chord` (with inversion notation: "Dm 64") |
| `cadences` | Implicit from chord progression |
| Voice ranges in `music_utils.RANGE` | `chord_chart.ranges[voice].lo/hi` |

The translation between formats is mechanical.
