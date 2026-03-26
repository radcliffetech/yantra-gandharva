# Algorithmic Engine Examples

These files were generated entirely by the algorithmic engine (`--engine algorithmic`) — no LLM or API key required. Each JSON file has a corresponding MusicXML file that can be opened in Dorico, MuseScore, or any notation software.

## Partimento

### Romanesca in C major (8 bars)

Prompt: `"8 bars in C major, Romanesca then Prinner"`

| File | Description |
|------|-------------|
| `partimento_romanesca_c.json` | Bassline + figured bass |
| `partimento_romanesca_c.musicxml` | Bassline as notation |
| `realized_romanesca_c.json` | SATB realization (soprano, alto, tenor, bass) |
| `realized_romanesca_c.musicxml` | Four-part score |
| `review_partimento_romanesca_c.json` | Rule-based critique of the bassline |
| `review_realization_romanesca_c.json` | Rule-based critique of the SATB voicing |

### Rule of the Octave in D minor (12 bars)

Prompt: `"Rule of the Octave in D minor, 12 bars"`

| File | Description |
|------|-------------|
| `partimento_roo_d_minor.json` | Bassline + figured bass |
| `partimento_roo_d_minor.musicxml` | Bassline as notation |
| `realized_roo_d_minor.json` | SATB realization |
| `realized_roo_d_minor.musicxml` | Four-part score |

## Jazz

### 12-Bar Blues in F

Prompt: `"12-bar blues in F"`

| File | Description |
|------|-------------|
| `jazz_blues_f.json` | Melody + chord symbols |
| `jazz_blues_f.musicxml` | Lead sheet |

### Rhythm Changes in Bb (32-bar AABA)

Prompt: `"rhythm changes in Bb"`

| File | Description |
|------|-------------|
| `jazz_rhythm_changes_bb.json` | Melody + chord symbols |
| `jazz_rhythm_changes_bb.musicxml` | Lead sheet |

## Reproducing

```bash
# Partimento
yantra generate-partimento "8 bars in C major, Romanesca then Prinner" --engine algorithmic
yantra realize-partimento partimento.json --engine algorithmic

# Jazz
yantra generate-lead-sheet "12-bar blues in F" --engine algorithmic
yantra generate-lead-sheet "rhythm changes in Bb" --engine algorithmic
```
