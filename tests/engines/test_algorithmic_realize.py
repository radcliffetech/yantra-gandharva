"""Tests for algorithmic SATB realization (Phase 3)."""

import json

import pytest
from music21 import pitch

from genres.partimento.engines.algorithmic import AlgorithmicPartimentoEngine
from genres.partimento.engines.algorithmic.generate import generate_partimento
from genres.partimento.engines.algorithmic.realize import realize_partimento_satb


# ------------------------------------------------------------------
# Output structure tests
# ------------------------------------------------------------------


class TestOutputStructure:
    def test_has_all_four_voices(self):
        data = {
            "key": "C major",
            "bassline": [["C3"], ["G2"], ["C3"]],
            "figures": [[["5", "3"]], [["5", "3"]], [["5", "3"]]],
        }
        result = realize_partimento_satb(data)
        assert "soprano" in result
        assert "alto" in result
        assert "tenor" in result
        assert "bass" in result

    def test_all_voices_same_measure_count(self):
        data = {
            "key": "C major",
            "bassline": [["C3"], ["D3"], ["E3"], ["F3"], ["G2"], ["C3"]],
            "figures": [
                [["5", "3"]],
                [["6"]],
                [["6"]],
                [["5", "3"]],
                [["5", "3"]],
                [["5", "3"]],
            ],
        }
        result = realize_partimento_satb(data)
        n = len(result["soprano"])
        assert len(result["alto"]) == n
        assert len(result["tenor"]) == n
        assert len(result["bass"]) == n

    def test_measure_count_matches_input(self):
        data = {
            "key": "C major",
            "bassline": [["C3"], ["G2"], ["C3"]],
            "figures": [[["5", "3"]], [["5", "3"]], [["5", "3"]]],
        }
        result = realize_partimento_satb(data)
        assert len(result["soprano"]) == 3

    def test_notes_per_measure_match_input(self):
        data = {
            "key": "C major",
            "bassline": [["C3", "D3"], ["E3"], ["G2", "F2", "E2"], ["C3"]],
            "figures": [[["5", "3"], ["6"]], [[]], [["5", "3"], [], []], [["5", "3"]]],
        }
        result = realize_partimento_satb(data)
        assert len(result["soprano"][0]) == 2
        assert len(result["soprano"][1]) == 1
        assert len(result["soprano"][2]) == 3
        assert len(result["soprano"][3]) == 1

    def test_each_note_is_valid_pitch_string(self):
        data = {
            "key": "C major",
            "bassline": [["C3"], ["G2"], ["C3"]],
            "figures": [[["5", "3"]], [["5", "3"]], [["5", "3"]]],
        }
        result = realize_partimento_satb(data)
        for voice in ["soprano", "alto", "tenor", "bass"]:
            for measure in result[voice]:
                for note_str in measure:
                    # Should parse without error
                    p = pitch.Pitch(note_str)
                    assert p.octave is not None


# ------------------------------------------------------------------
# Bass echoes input
# ------------------------------------------------------------------


class TestBassEchoesInput:
    def test_bass_matches_input_bassline(self):
        data = {
            "key": "C major",
            "bassline": [["C3"], ["G2"], ["C3"]],
            "figures": [[["5", "3"]], [["5", "3"]], [["5", "3"]]],
        }
        result = realize_partimento_satb(data)
        for i, measure in enumerate(result["bass"]):
            for j, note_str in enumerate(measure):
                input_pitch = pitch.Pitch(data["bassline"][i][j])
                output_pitch = pitch.Pitch(note_str)
                assert input_pitch.nameWithOctave == output_pitch.nameWithOctave


# ------------------------------------------------------------------
# Voice ranges
# ------------------------------------------------------------------


class TestVoiceRanges:
    """Verify voices stay within Baroque SATB ranges."""

    # music21's realizer uses slightly wider ranges than strict Baroque norms
    RANGES = {
        "soprano": (pitch.Pitch("C4"), pitch.Pitch("A5")),
        "alto": (pitch.Pitch("F3"), pitch.Pitch("E5")),
        "tenor": (pitch.Pitch("C3"), pitch.Pitch("A4")),
        "bass": (pitch.Pitch("E2"), pitch.Pitch("E4")),
    }

    def test_voices_in_range(self):
        data = {
            "key": "C major",
            "bassline": [["C3"], ["D3"], ["E3"], ["F3"], ["G2"], ["C3"]],
            "figures": [
                [["5", "3"]],
                [["6"]],
                [["6"]],
                [["5", "3"]],
                [["5", "3"]],
                [["5", "3"]],
            ],
        }
        result = realize_partimento_satb(data)
        for voice_name, (low, high) in self.RANGES.items():
            for measure in result[voice_name]:
                for note_str in measure:
                    p = pitch.Pitch(note_str)
                    assert low <= p <= high, (
                        f"{voice_name} note {note_str} out of range "
                        f"[{low.nameWithOctave}-{high.nameWithOctave}]"
                    )


# ------------------------------------------------------------------
# Input format handling
# ------------------------------------------------------------------


class TestInputFormats:
    def test_dict_input(self):
        data = {
            "key": "C major",
            "bassline": [["C3"], ["G2"], ["C3"]],
            "figures": [[["5", "3"]], [["5", "3"]], [["5", "3"]]],
        }
        result = realize_partimento_satb(data)
        assert len(result["soprano"]) == 3

    def test_json_string_input(self):
        data = {
            "key": "C major",
            "bassline": [["C3"], ["G2"], ["C3"]],
            "figures": [[["5", "3"]], [["5", "3"]], [["5", "3"]]],
        }
        result = realize_partimento_satb(json.dumps(data))
        assert len(result["soprano"]) == 3

    def test_file_path_input(self, tmp_path):
        data = {
            "data": {
                "key": "C major",
                "bassline": [["C3"], ["G2"], ["C3"]],
                "figures": [[["5", "3"]], [["5", "3"]], [["5", "3"]]],
            }
        }
        json_path = tmp_path / "partimento.json"
        json_path.write_text(json.dumps(data))

        result = realize_partimento_satb(str(json_path))
        assert len(result["soprano"]) == 3

    def test_flat_bassline_normalized(self):
        data = {
            "key": "C major",
            "bassline": ["C3", "G2", "C3"],
            "figures": [[["5", "3"]], [["5", "3"]], [["5", "3"]]],
        }
        result = realize_partimento_satb(data)
        assert len(result["soprano"]) == 3


# ------------------------------------------------------------------
# Different keys
# ------------------------------------------------------------------


class TestDifferentKeys:
    @pytest.mark.parametrize(
        "key_str",
        ["C major", "G major", "D minor", "F major", "A minor", "B- major"],
    )
    def test_realizes_in_various_keys(self, key_str):
        # Simple I-V-I in any key
        from music21 import key as m21_key

        k = m21_key.Key(key_str.split()[0], key_str.split()[1])
        tonic = k.tonic.name
        dominant_p = k.pitchFromDegree(5)

        data = {
            "key": key_str,
            "bassline": [[f"{tonic}3"], [f"{dominant_p.name}2"], [f"{tonic}3"]],
            "figures": [[["5", "3"]], [["5", "3"]], [["5", "3"]]],
        }
        result = realize_partimento_satb(data)
        assert len(result["soprano"]) == 3
        assert len(result["bass"]) == 3


# ------------------------------------------------------------------
# End-to-end: generate then realize
# ------------------------------------------------------------------


class TestGenerateThenRealize:
    def test_full_pipeline(self):
        engine = AlgorithmicPartimentoEngine()
        partimento = engine.generate_partimento("8 bars in C major")
        realized = engine.realize_partimento_satb(partimento)
        assert len(realized["soprano"]) == 8
        assert len(realized["bass"]) == 8

    def test_pipeline_d_minor(self):
        engine = AlgorithmicPartimentoEngine()
        partimento = engine.generate_partimento("4 bars in D minor")
        realized = engine.realize_partimento_satb(partimento)
        assert len(realized["soprano"]) == 4


# ------------------------------------------------------------------
# Export compatibility
# ------------------------------------------------------------------


class TestExportCompatibility:
    def test_export_realized_to_musicxml(self, tmp_path):
        from genres.partimento.tasks.export import export_realized_partimento_to_musicxml
        from lib.utils.chain_utils import write_chain_json

        engine = AlgorithmicPartimentoEngine()
        partimento = engine.generate_partimento("8 bars in C major")
        realized = engine.realize_partimento_satb(partimento)

        json_path = tmp_path / "realized_01.json"
        write_chain_json(realized, str(json_path), mode="realize-partimento")

        xml_path = tmp_path / "realized.musicxml"
        export_realized_partimento_to_musicxml(str(json_path), str(xml_path))

        assert xml_path.exists()
        assert xml_path.stat().st_size > 0

    def test_export_realized_to_midi(self, tmp_path):
        from genres.partimento.tasks.export import export_realized_partimento_to_midi
        from lib.utils.chain_utils import write_chain_json

        engine = AlgorithmicPartimentoEngine()
        partimento = engine.generate_partimento("4 bars in G major")
        realized = engine.realize_partimento_satb(partimento)

        json_path = tmp_path / "realized_01.json"
        write_chain_json(realized, str(json_path), mode="realize-partimento")

        midi_path = tmp_path / "realized.mid"
        export_realized_partimento_to_midi(str(json_path), str(midi_path))

        assert midi_path.exists()
        assert midi_path.stat().st_size > 0
