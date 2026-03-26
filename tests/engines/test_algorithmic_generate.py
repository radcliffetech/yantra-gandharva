"""Tests for algorithmic partimento generation (Phase 2)."""

import json
import tempfile
from pathlib import Path

import pytest
from music21 import key, pitch

from genres.partimento.engines.algorithmic import AlgorithmicPartimentoEngine
from genres.partimento.engines.algorithmic.generate import generate_partimento
from genres.partimento.engines.algorithmic.prompt_parser import parse_prompt
from genres.partimento.engines.algorithmic.schemata import (
    SCHEMATA,
    cadence_authentic,
    cadence_half,
    fonte,
    monte,
    prinner,
    romanesca,
    rule_of_octave_ascending,
    rule_of_octave_descending,
    transpose_pattern,
)


# ------------------------------------------------------------------
# Schemata unit tests
# ------------------------------------------------------------------


class TestTransposition:
    def test_c_to_c_is_identity(self):
        notes = ["C", "D", "E"]
        result = transpose_pattern(notes, key.Key("C"), key.Key("C"))
        assert result == ["C", "D", "E"]

    def test_c_to_g(self):
        notes = ["C", "E", "G"]
        result = transpose_pattern(notes, key.Key("C"), key.Key("G"))
        assert result == ["G", "B", "D"]

    def test_c_to_f(self):
        notes = ["C", "D", "E"]
        result = transpose_pattern(notes, key.Key("C"), key.Key("F"))
        assert result == ["F", "G", "A"]

    def test_c_to_d(self):
        notes = ["C", "G"]
        result = transpose_pattern(notes, key.Key("C"), key.Key("D"))
        assert result == ["D", "A"]


class TestSchemaStructure:
    """Every schema must return the correct structure."""

    @pytest.mark.parametrize("name", list(SCHEMATA.keys()))
    def test_schema_returns_required_keys(self, name):
        result = SCHEMATA[name]()
        assert "bass" in result
        assert "figures" in result
        assert "bars" in result
        assert "cadence" in result

    @pytest.mark.parametrize("name", list(SCHEMATA.keys()))
    def test_bass_and_figures_same_length(self, name):
        result = SCHEMATA[name]()
        assert len(result["bass"]) == len(result["figures"])

    @pytest.mark.parametrize("name", list(SCHEMATA.keys()))
    def test_bars_matches_bass_length(self, name):
        result = SCHEMATA[name]()
        assert result["bars"] == len(result["bass"])


class TestSchemaContent:
    def test_romanesca_in_c(self):
        r = romanesca()
        assert r["bass"] == ["C", "B", "A", "G"]
        assert r["bars"] == 4
        assert r["cadence"] is None

    def test_romanesca_in_g(self):
        r = romanesca(key.Key("G"))
        assert r["bass"] == ["G", "F#", "E", "D"]

    def test_prinner_in_c(self):
        p = prinner()
        assert p["bass"] == ["A", "G", "F", "E"]
        assert p["bars"] == 4

    def test_monte_in_c(self):
        m = monte()
        assert m["bass"] == ["D", "G", "E", "A"]

    def test_fonte_in_c(self):
        f = fonte()
        assert f["bass"] == ["A", "D", "G", "C"]
        assert f["bars"] == 4

    def test_rule_of_octave_ascending_length(self):
        roo = rule_of_octave_ascending()
        assert roo["bars"] == 8
        assert len(roo["bass"]) == 8

    def test_rule_of_octave_descending_length(self):
        roo = rule_of_octave_descending()
        assert roo["bars"] == 8

    def test_cadence_authentic(self):
        c = cadence_authentic()
        assert c["bass"] == ["G", "C"]
        assert c["cadence"] == "authentic cadence"
        assert c["bars"] == 2

    def test_cadence_half(self):
        c = cadence_half()
        assert c["bass"] == ["C", "G"]
        assert c["cadence"] == "half cadence"

    def test_cadence_in_d(self):
        c = cadence_authentic(key.Key("D"))
        assert c["bass"] == ["A", "D"]


# ------------------------------------------------------------------
# Prompt parser tests
# ------------------------------------------------------------------


class TestPromptParser:
    def test_parse_key_major(self):
        result = parse_prompt("8 bars in D major")
        assert result["key"].tonic.name == "D"
        assert result["key"].mode == "major"

    def test_parse_key_minor(self):
        result = parse_prompt("in A minor, 4 bars")
        assert result["key"].tonic.name == "A"
        assert result["key"].mode == "minor"

    def test_parse_key_flat(self):
        result = parse_prompt("8 bars in Bb major")
        assert result["key"].tonic.name == "B-"

    def test_parse_key_sharp(self):
        result = parse_prompt("in F# minor")
        assert result["key"].tonic.name == "F#"
        assert result["key"].mode == "minor"

    def test_parse_key_default(self):
        result = parse_prompt("make me a partimento")
        assert result["key"].tonic.name == "C"
        assert result["key"].mode == "major"

    def test_parse_bars(self):
        result = parse_prompt("16 bars in C major")
        assert result["bars"] == 16

    def test_parse_bars_measures_synonym(self):
        result = parse_prompt("12 measures in G minor")
        assert result["bars"] == 12

    def test_parse_bars_default(self):
        result = parse_prompt("in D major")
        assert result["bars"] == 8

    def test_parse_style_bach(self):
        result = parse_prompt("in the style of Bach, 8 bars")
        assert result["style"] == "J. S. Bach"

    def test_parse_style_furno_default(self):
        result = parse_prompt("8 bars in C")
        assert result["style"] == "Furno"

    def test_parse_schemata_romanesca(self):
        result = parse_prompt("Romanesca then Prinner in D major")
        assert "romanesca" in result["schemata"]
        assert "prinner" in result["schemata"]

    def test_parse_schemata_rule_of_octave(self):
        result = parse_prompt("rule of the octave in C major")
        assert "rule_of_octave_ascending" in result["schemata"]

    def test_parse_cadence_half(self):
        result = parse_prompt("end with half cadence")
        assert result["cadence_type"] == "half"

    def test_parse_cadence_default_authentic(self):
        result = parse_prompt("8 bars in C")
        assert result["cadence_type"] == "authentic"


# ------------------------------------------------------------------
# End-to-end generation tests
# ------------------------------------------------------------------


class TestGeneratePartimento:
    def test_output_has_required_keys(self):
        result = generate_partimento("8 bars in C major")
        assert "title" in result
        assert "key" in result
        assert "bassline" in result
        assert "figures" in result
        assert "cadences" in result
        assert "style" in result
        assert "modulations" in result

    def test_output_bar_count_matches(self):
        result = generate_partimento("8 bars in C major")
        assert len(result["bassline"]) == 8

    def test_output_bassline_figures_parallel(self):
        result = generate_partimento("8 bars in D minor")
        assert len(result["bassline"]) == len(result["figures"])

    def test_key_in_output(self):
        result = generate_partimento("8 bars in D minor")
        assert "D" in result["key"]
        assert "minor" in result["key"]

    def test_has_cadence(self):
        result = generate_partimento("8 bars in C major")
        assert len(result["cadences"]) >= 1
        assert any("cadence" in c for c in result["cadences"])

    def test_style_recorded(self):
        result = generate_partimento("Bach style, 8 bars")
        assert "J. S. Bach" in result["style"]

    def test_bassline_notes_are_valid(self):
        result = generate_partimento("8 bars in C major")
        for measure in result["bassline"]:
            for note_str in measure:
                # Should parse without error
                p = pitch.Pitch(note_str)
                # Should be in bass range
                assert pitch.Pitch("C2") <= p <= pitch.Pitch("C4")

    def test_figures_are_lists_of_strings(self):
        result = generate_partimento("8 bars in C major")
        for measure_figs in result["figures"]:
            for fig_group in measure_figs:
                assert isinstance(fig_group, list)
                for fig in fig_group:
                    assert isinstance(fig, str)

    def test_4_bar_piece(self):
        result = generate_partimento("4 bars in C major")
        assert len(result["bassline"]) == 4

    def test_16_bar_piece(self):
        result = generate_partimento("16 bars in G major")
        assert len(result["bassline"]) == 16

    def test_with_explicit_schemata(self):
        result = generate_partimento("Romanesca in D major, 8 bars")
        assert len(result["bassline"]) == 8

    def test_modulations_is_empty_list(self):
        result = generate_partimento("8 bars in C major")
        assert result["modulations"] == []


class TestEngineIntegration:
    """Test through the AlgorithmicPartimentoEngine class."""

    def test_generate_via_engine(self):
        engine = AlgorithmicPartimentoEngine()
        result = engine.generate_partimento("8 bars in C major")
        assert result["title"] == "Partimento in C"
        assert len(result["bassline"]) == 8

    def test_realize_is_implemented(self):
        engine = AlgorithmicPartimentoEngine()
        partimento = engine.generate_partimento("4 bars in C major")
        result = engine.realize_partimento_satb(partimento)
        assert "soprano" in result
        assert len(result["soprano"]) == 4


class TestExportCompatibility:
    """Verify algorithmic output can be consumed by the export pipeline."""

    def test_export_to_musicxml(self, tmp_path):
        from lib.utils.chain_utils import write_chain_json
        from genres.partimento.tasks.export import export_partimento_to_musicxml

        result = generate_partimento("8 bars in C major")

        # Write through chain utils (as handlers do)
        json_path = tmp_path / "partimento_01.json"
        write_chain_json(result, str(json_path), mode="generate-partimento")

        # Export to MusicXML
        xml_path = tmp_path / "partimento.musicxml"
        export_partimento_to_musicxml(str(json_path), str(xml_path))

        assert xml_path.exists()
        assert xml_path.stat().st_size > 0

    def test_export_to_midi(self, tmp_path):
        from lib.utils.chain_utils import write_chain_json
        from genres.partimento.tasks.export import export_partimento_to_midi

        result = generate_partimento("4 bars in D minor")

        json_path = tmp_path / "partimento_01.json"
        write_chain_json(result, str(json_path), mode="generate-partimento")

        midi_path = tmp_path / "partimento.mid"
        export_partimento_to_midi(str(json_path), str(midi_path))

        assert midi_path.exists()
        assert midi_path.stat().st_size > 0
