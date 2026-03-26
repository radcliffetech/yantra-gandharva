"""Tests for algorithmic jazz lead sheet generation (Phase 5)."""

import argparse
import json

import pytest
from music21 import pitch

from genres.jazz.engines import get_jazz_engine
from genres.jazz.engines.algorithmic import AlgorithmicJazzEngine
from genres.jazz.engines.algorithmic.generate import generate_jazz_lead_sheet
from genres.jazz.engines.algorithmic.templates import (
    TEMPLATES,
    blues_12bar,
    blues_minor_12bar,
    ii_v_i_extended_8bar,
    ii_v_i_turnaround,
    rhythm_changes_32bar,
    standard_16bar,
    transpose_chords,
    transpose_melody,
)
from engines import EngineType


# ------------------------------------------------------------------
# Template unit tests
# ------------------------------------------------------------------


class TestTemplateStructure:
    @pytest.mark.parametrize("name", list(TEMPLATES.keys()))
    def test_template_returns_required_keys(self, name):
        t = TEMPLATES[name]()
        assert "chords" in t
        assert "melody" in t
        assert "bars" in t
        assert "form" in t
        assert "ref_key" in t

    @pytest.mark.parametrize("name", list(TEMPLATES.keys()))
    def test_chords_and_melody_same_length(self, name):
        t = TEMPLATES[name]()
        assert len(t["chords"]) == len(t["melody"])

    @pytest.mark.parametrize("name", list(TEMPLATES.keys()))
    def test_bars_matches_length(self, name):
        t = TEMPLATES[name]()
        assert t["bars"] == len(t["chords"])


class TestTemplateContent:
    def test_blues_is_12_bars(self):
        t = blues_12bar()
        assert t["bars"] == 12

    def test_blues_starts_on_tonic(self):
        t = blues_12bar()
        assert t["chords"][0] == "C7"

    def test_minor_blues_is_12_bars(self):
        t = blues_minor_12bar()
        assert t["bars"] == 12

    def test_rhythm_changes_is_32_bars(self):
        t = rhythm_changes_32bar()
        assert t["bars"] == 32

    def test_rhythm_changes_aaba_form(self):
        t = rhythm_changes_32bar()
        # A sections (0-7, 8-15) should have same chords
        assert t["chords"][:8] == t["chords"][8:16]
        # Last A section (24-31) should match first
        assert t["chords"][:8] == t["chords"][24:32]

    def test_standard_is_16_bars(self):
        t = standard_16bar()
        assert t["bars"] == 16

    def test_turnaround_is_4_bars(self):
        t = ii_v_i_turnaround()
        assert t["bars"] == 4

    def test_ii_v_i_is_8_bars(self):
        t = ii_v_i_extended_8bar()
        assert t["bars"] == 8


# ------------------------------------------------------------------
# Transposition tests
# ------------------------------------------------------------------


class TestTransposition:
    def test_transpose_chords_c_to_f(self):
        chords = ["C7", "F7", "G7"]
        result = transpose_chords(chords, "C", "F")
        assert result == ["F7", "B-7", "C7"]

    def test_transpose_chords_identity(self):
        chords = ["Cmaj7", "Dm7", "G7"]
        result = transpose_chords(chords, "C", "C")
        assert result == chords

    def test_transpose_melody_c_to_g(self):
        melody = ["C4", "E4", "G4"]
        result = transpose_melody(melody, "C", "G")
        # C->G, E->B, G->D
        assert len(result) == 3
        for note_str in result:
            pitch.Pitch(note_str)  # should parse without error


# ------------------------------------------------------------------
# Prompt parsing tests
# ------------------------------------------------------------------


class TestPromptParsing:
    def test_key_extraction(self):
        result = generate_jazz_lead_sheet("blues in F")
        assert result["key"] == "F"

    def test_key_with_flat(self):
        result = generate_jazz_lead_sheet("blues in Bb")
        assert result["key"] == "Bb"

    def test_key_default_c(self):
        result = generate_jazz_lead_sheet("just a blues")
        assert result["key"] == "C"

    def test_blues_form_detected(self):
        result = generate_jazz_lead_sheet("12-bar blues in C")
        assert len(result["chords"]) == 12

    def test_rhythm_changes_detected(self):
        result = generate_jazz_lead_sheet("rhythm changes in C")
        assert len(result["chords"]) == 32

    def test_standard_form_detected(self):
        result = generate_jazz_lead_sheet("16-bar standard in C")
        assert len(result["chords"]) == 16

    def test_minor_blues_detected(self):
        result = generate_jazz_lead_sheet("minor blues in C")
        assert len(result["chords"]) == 12
        assert "m" in result["chords"][0].lower()

    def test_meter_default_4_4(self):
        result = generate_jazz_lead_sheet("blues in C")
        assert result["meter"] == "4/4"

    def test_custom_bar_count(self):
        result = generate_jazz_lead_sheet("8 bars of blues in C")
        assert len(result["chords"]) == 8


# ------------------------------------------------------------------
# Output contract tests
# ------------------------------------------------------------------


class TestOutputContract:
    def test_has_required_keys(self):
        result = generate_jazz_lead_sheet("blues in F")
        assert "title" in result
        assert "key" in result
        assert "meter" in result
        assert "melody" in result
        assert "chords" in result

    def test_melody_chords_same_length(self):
        result = generate_jazz_lead_sheet("blues in F")
        assert len(result["melody"]) == len(result["chords"])

    def test_melody_notes_are_valid(self):
        result = generate_jazz_lead_sheet("blues in F")
        for note_str in result["melody"]:
            p = pitch.Pitch(note_str)
            assert p.octave is not None

    def test_title_contains_key(self):
        result = generate_jazz_lead_sheet("blues in F")
        assert "F" in result["title"]


# ------------------------------------------------------------------
# Engine integration tests
# ------------------------------------------------------------------


class TestEngineIntegration:
    def test_generate_via_engine(self):
        engine = AlgorithmicJazzEngine()
        result = engine.generate_jazz_lead_sheet("blues in C")
        assert len(result["chords"]) == 12

    def test_factory_returns_algorithmic(self):
        engine = get_jazz_engine(EngineType.ALGORITHMIC)
        assert isinstance(engine, AlgorithmicJazzEngine)


# ------------------------------------------------------------------
# Export compatibility tests
# ------------------------------------------------------------------


class TestExportCompatibility:
    def test_export_to_musicxml(self, tmp_path):
        from genres.jazz.tasks.export import export_lead_sheet

        result = generate_jazz_lead_sheet("blues in F")

        json_path = tmp_path / "lead_sheet.json"
        json_path.write_text(json.dumps(result))

        xml_path = tmp_path / "lead_sheet.musicxml"
        export_lead_sheet(str(json_path), str(xml_path))

        assert xml_path.exists()
        assert xml_path.stat().st_size > 0

    def test_various_forms_export(self, tmp_path):
        """All template forms should export cleanly."""
        from genres.jazz.tasks.export import export_lead_sheet

        for form in ["blues", "rhythm changes", "16-bar standard", "minor blues"]:
            result = generate_jazz_lead_sheet(f"{form} in C")
            json_path = tmp_path / f"{form.replace(' ', '_')}.json"
            json_path.write_text(json.dumps(result))

            xml_path = json_path.with_suffix(".musicxml")
            export_lead_sheet(str(json_path), str(xml_path))
            assert xml_path.exists()


# ------------------------------------------------------------------
# CLI flag test
# ------------------------------------------------------------------


class TestJazzCliFlag:
    def test_generate_lead_sheet_has_engine_flag(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        from cli.commands.jazz import register_generate_lead_sheet

        register_generate_lead_sheet(subparsers)

        args = parser.parse_args(
            ["generate-lead-sheet", "blues in F", "--engine", "algorithmic"]
        )
        assert args.engine == "algorithmic"

    def test_generate_lead_sheet_default_llm(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        from cli.commands.jazz import register_generate_lead_sheet

        register_generate_lead_sheet(subparsers)

        args = parser.parse_args(["generate-lead-sheet", "blues in F"])
        assert args.engine == "llm"
