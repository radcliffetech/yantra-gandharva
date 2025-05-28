# 🛣️ Yantra Gandharva Roadmap

> “Where structure meets spirit.”  
> A living roadmap for expanding the celestial machine.

---

## 🎼 Core Features

- [x] JSON → MusicXML pipeline for jazz and figured bass
- [x] CLI for generating and rendering scores
- [x] LLM-backed prompt-based realization engine
- [x] CI/CD with linting and formatting
- [x] Pre-commit hooks for code hygiene
- [x] MusicXML inspection and summarization via CLI
- [x] CLI command for chaining prompt → JSON → MusicXML in one go
- [x] Export to MIDI
- [ ] Partial score playback preview (e.g. bassline only)
- [ ] Score version comparison tool (original vs patched JSON)

---

## 🎵 Musical Domains

### Jazz
- [x] Jazz lead sheet generation from prompt
- [ ] Swing rhythm annotations
- [ ] Basic piano comping pattern output
- [ ] Lyrics
- [ ] Complex forms (AABA, rhythm changes)
- [ ] MIDI voicings with slash notation

### Baroque / Classical
- [x] Figured bass realization (Claudio Furno)
- [x] Partimento generator
- [x] First species counterpoint (SATB)
- [x] Chorale-style four-part harmonization
- [x] Reharmonization via LLM review
- [x] Partimento realization with LLM patch review
- [ ] Multi-species counterpoint chaining
- [ ] Voice-leading validator (rules + LLM)

### Experimental
- [ ] Prompt-based aleatoric score generation
- [ ] Modal, non-functional harmony support
- [ ] "Wrong but interesting" partimenti / realizations

---

## 🧠 Language + Semantics

- [x] Pluggable LLM system with mockable `call_llm` function
- [x] Score review: have the LLM critique generated MusicXML
- [x] Suggested patch generation and auto-application
- [x] Critique self-play: prompt → review → revise → re-review
- [ ] Style transfer in prompts (e.g. realize like J.S. Bach)
- [ ] Student feedback mode: critique as if grading a student
- [ ] Prompt playground and prompt scoring tools

---

## 🖥️ Interfaces

- [x] CLI (Remix-style)
- [x] Tab-completion via argcomplete
- [ ] Web UI for uploading prompts / downloading scores
- [ ] JSON viewer/editor for reviewing realizations
- [ ] Interactive score editor with MusicXML/MIDI preview
- [ ] Text-based UI (TUI) for feedback loop control

---

## 📚 Documentation

- [x] README with examples, structure, and badges
- [x] Developer guide with setup steps
- [ ] User guide for CLI and input formats
- [ ] JSON schema documentation
- [ ] Glossary of musical terms used in prompts
- [ ] Prompt crafting tips for different musical styles

---

## 🌍 Outreach & Publishing

- [ ] Demo videos (score-to-sound walkthrough)
- [ ] Website or blog for examples and updates
- [ ] Gallery of visual scores and prompt samples
- [ ] Option to share scores via GitHub Pages
- [ ] Notion archive or digital zine of best-of generations

---

## 🌱 Long-Term

- [ ] Plugin or extension for Dorico / MuseScore
- [ ] Adaptive AI (learn from human-edited scores)
- [ ] Support for orchestral or ensemble textures
- [ ] Real-time prompt-to-audio playback engine (Web MIDI or VST)
- [ ] Score alignment with audio for synced learning