# 🧠 How to Generate and Upload a Partimento Realization

This guide walks through the process of generating, realizing, exporting, and uploading a partimento exercise using Yantra Gandharva.

## 📦 Input Requirements

You need a JSON file representing a partimento prompt. A sample is available at:

```
data/examples/furno_example.json
```

## ⚙️ Step 1: Realize the Initial Partimento

```bash
yantra realize-partimento data/examples/furno_example.json --output generated/chains/partimento_furno_demo
```

This creates a chain directory and writes:
- `partimento.json`
- `realized.json`
- `metadata.json`

## 📝 Step 2: Review the Realization

Review the SATB realization:

```bash
yantra review-score generated/chains/partimento_furno_demo/realized.json --output generated/chains/partimento_furno_demo
```

This writes `review_realization_1.json` into the chain directory and updates metadata.

## 🛠️ Step 3: Revise the Realization

If the review contains a suggested patch, you can apply it:

```bash
yantra revise-realization generated/chains/partimento_furno_demo/realized.json generated/chains/partimento_furno_demo/review_realization_1.json --output generated/chains/partimento_furno_demo
```

This creates `realized_2.json`.

## 💾 Step 4: Export to MusicXML, MIDI, and OGG

```bash
yantra export-realization generated/chains/partimento_furno_demo/realized.json --output generated/chains/partimento_furno_demo
```

This writes:
- `realized.musicxml`
- `realized.mid`
- `realized.ogg`

## ☁️ Step 5: Upload to Firebase

Once you're satisfied with the result, push it to Firebase:

```bash
yantra push-chain generated/chains/partimento_furno_demo
```

## 🔍 Optional: List All Uploaded Realizations

```bash
yantra list-realizations
```
