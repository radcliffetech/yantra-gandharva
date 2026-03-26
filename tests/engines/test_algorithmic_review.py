"""Tests for algorithmic review of partimenti and SATB realizations (Phase 4)."""

import json

import pytest

from genres.partimento.engines.algorithmic import AlgorithmicPartimentoEngine
from genres.partimento.engines.algorithmic.review import (
    review_partimento,
    review_realized_score,
)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _write_chain_json(tmp_path, filename, data):
    """Write a chain-wrapped JSON file for testing."""
    path = tmp_path / filename
    path.write_text(json.dumps({"data": data}))
    return str(path)


# ------------------------------------------------------------------
# Partimento review
# ------------------------------------------------------------------


class TestPartimentoReviewContract:
    """Verify the review output matches the JSON contract."""

    def test_output_is_valid_json(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "p.json",
            {
                "key": "C major",
                "bassline": [["C3"], ["G2"], ["C3"]],
                "figures": [[["5", "3"]], [["5", "3"]], [["5", "3"]]],
                "cadences": ["measure 3: authentic cadence"],
            },
        )
        result = json.loads(review_partimento(path))
        assert isinstance(result, dict)

    def test_has_required_keys(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "p.json",
            {
                "key": "C major",
                "bassline": [["C3"], ["G2"], ["C3"]],
                "figures": [[["5", "3"]], [["5", "3"]], [["5", "3"]]],
                "cadences": ["measure 3: authentic cadence"],
            },
        )
        result = json.loads(review_partimento(path))
        assert "message" in result
        assert "strengths" in result
        assert "issues" in result

    def test_strengths_are_dicts_with_aspect_description(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "p.json",
            {
                "key": "C major",
                "bassline": [["C3"], ["D3"], ["E3"], ["G2"], ["C3"]],
                "figures": [
                    [["5", "3"]],
                    [["6"]],
                    [["6"]],
                    [["5", "3"]],
                    [["5", "3"]],
                ],
                "cadences": ["measure 5: authentic cadence"],
            },
        )
        result = json.loads(review_partimento(path))
        for s in result["strengths"]:
            assert "aspect" in s
            assert "description" in s


class TestPartimentoReviewClean:
    def test_clean_partimento_no_issues(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "p.json",
            {
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
                "cadences": ["measure 6: authentic cadence"],
            },
        )
        result = json.loads(review_partimento(path))
        assert result["issues"] == []
        assert any("no" in s["description"].lower() for s in result["strengths"])


class TestPartimentoReviewDetectsIssues:
    def test_detects_awkward_leap(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "p.json",
            {
                "key": "C major",
                "bassline": [["C2"], ["C4"]],  # > octave leap
                "figures": [[[]], [[]]],
                "cadences": ["measure 2: authentic cadence"],
            },
        )
        result = json.loads(review_partimento(path))
        assert any("leap" in i.lower() for i in result["issues"])

    def test_detects_missing_cadences(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "p.json",
            {
                "key": "C major",
                "bassline": [["C3"], ["D3"], ["E3"], ["F3"]],
                "figures": [[[]], [[]], [[]], [[]]],
                "cadences": [],
            },
        )
        result = json.loads(review_partimento(path))
        assert any("cadence" in i.lower() for i in result["issues"])

    def test_detects_out_of_range(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "p.json",
            {
                "key": "C major",
                "bassline": [["C1"], ["G2"]],  # C1 is below bass range
                "figures": [[[]], [[]]],
                "cadences": ["measure 2: authentic cadence"],
            },
        )
        result = json.loads(review_partimento(path))
        assert any("range" in i.lower() for i in result["issues"])

    def test_detects_monotony(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "p.json",
            {
                "key": "C major",
                "bassline": [["C3"], ["C3"], ["C3"], ["C3"], ["G2"], ["C3"]],
                "figures": [[[]], [[]], [[]], [[]], [[]], [[]]],
                "cadences": ["measure 6: authentic cadence"],
            },
        )
        result = json.loads(review_partimento(path))
        assert any("monoton" in i.lower() for i in result["issues"])

    def test_detects_no_strong_cadence(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "p.json",
            {
                "key": "C major",
                "bassline": [["C3"], ["D3"], ["E3"], ["G2"]],
                "figures": [[[]], [[]], [[]], [[]]],
                "cadences": ["measure 4: half cadence"],  # only half, no authentic
            },
        )
        result = json.loads(review_partimento(path))
        assert any("authentic" in i.lower() or "plagal" in i.lower() for i in result["issues"])


# ------------------------------------------------------------------
# SATB realization review
# ------------------------------------------------------------------


class TestRealizationReviewContract:
    def test_output_is_valid_json(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "r.json",
            {
                "key": "C major",
                "soprano": [["E5"], ["D5"], ["C5"]],
                "alto": [["C4"], ["B3"], ["E4"]],
                "tenor": [["G3"], ["G3"], ["G3"]],
                "bass": [["C3"], ["G2"], ["C3"]],
            },
        )
        result = json.loads(review_realized_score(path))
        assert "message" in result
        assert "strengths" in result
        assert "issues" in result

    def test_strengths_format(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "r.json",
            {
                "key": "C major",
                "soprano": [["E5"], ["D5"], ["C5"]],
                "alto": [["C4"], ["B3"], ["E4"]],
                "tenor": [["G3"], ["G3"], ["G3"]],
                "bass": [["C3"], ["G2"], ["C3"]],
            },
        )
        result = json.loads(review_realized_score(path))
        for s in result["strengths"]:
            assert "aspect" in s
            assert "description" in s


class TestRealizationReviewClean:
    def test_clean_realization_no_issues(self, tmp_path):
        # Well-spaced SATB voicing with no violations
        path = _write_chain_json(
            tmp_path,
            "r.json",
            {
                "key": "C major",
                "soprano": [["E5"], ["D5"], ["E5"]],
                "alto": [["G4"], ["G4"], ["G4"]],
                "tenor": [["C4"], ["B3"], ["C4"]],
                "bass": [["C3"], ["G2"], ["C3"]],
            },
        )
        result = json.loads(review_realized_score(path))
        assert result["issues"] == [], f"Unexpected issues: {result['issues']}"


class TestRealizationReviewDetectsIssues:
    def test_detects_voice_crossing(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "r.json",
            {
                "key": "C major",
                "soprano": [["C4"]],  # soprano below alto
                "alto": [["E5"]],
                "tenor": [["G3"]],
                "bass": [["C3"]],
            },
        )
        result = json.loads(review_realized_score(path))
        assert any("crossing" in i.lower() for i in result["issues"])

    def test_detects_spacing_violation(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "r.json",
            {
                "key": "C major",
                "soprano": [["A5"]],
                "alto": [["G3"]],  # > octave from soprano
                "tenor": [["E3"]],
                "bass": [["C3"]],
            },
        )
        result = json.loads(review_realized_score(path))
        assert any("spacing" in i.lower() for i in result["issues"])

    def test_detects_parallel_fifths(self, tmp_path):
        # Parallel 5ths: S-B both move from P5 to P5
        # m1: S=G4, B=C3 (P5) -> m2: S=A4, B=D3 (P5)
        path = _write_chain_json(
            tmp_path,
            "r.json",
            {
                "key": "C major",
                "soprano": [["G4"], ["A4"]],
                "alto": [["E4"], ["F4"]],
                "tenor": [["C4"], ["D4"]],
                "bass": [["C3"], ["D3"]],
            },
        )
        result = json.loads(review_realized_score(path))
        assert any("parallel" in i.lower() and "P5" in i for i in result["issues"])

    def test_detects_parallel_octaves(self, tmp_path):
        # Parallel 8ves: S-B both move from P8 to P8
        # m1: S=C4, B=C3 (P8) -> m2: S=D4, B=D3 (P8)
        path = _write_chain_json(
            tmp_path,
            "r.json",
            {
                "key": "C major",
                "soprano": [["C4"], ["D4"]],
                "alto": [["E4"], ["F4"]],
                "tenor": [["G3"], ["A3"]],
                "bass": [["C3"], ["D3"]],
            },
        )
        result = json.loads(review_realized_score(path))
        assert any("parallel" in i.lower() and ("P8" in i or "P1" in i) for i in result["issues"])

    def test_detects_out_of_range(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "r.json",
            {
                "key": "C major",
                "soprano": [["C6"]],  # above soprano range
                "alto": [["E4"]],
                "tenor": [["G3"]],
                "bass": [["C3"]],
            },
        )
        result = json.loads(review_realized_score(path))
        assert any("range" in i.lower() for i in result["issues"])

    def test_detects_doubled_leading_tone(self, tmp_path):
        # In C major, leading tone is B
        path = _write_chain_json(
            tmp_path,
            "r.json",
            {
                "key": "C major",
                "soprano": [["B4"]],
                "alto": [["B4"]],  # doubled leading tone
                "tenor": [["G3"]],
                "bass": [["G2"]],
            },
        )
        result = json.loads(review_realized_score(path))
        assert any("leading tone" in i.lower() for i in result["issues"])

    def test_has_suggested_patch_when_issues(self, tmp_path):
        path = _write_chain_json(
            tmp_path,
            "r.json",
            {
                "key": "C major",
                "soprano": [["C4"]],  # crossing with alto
                "alto": [["E5"]],
                "tenor": [["G3"]],
                "bass": [["C3"]],
            },
        )
        result = json.loads(review_realized_score(path))
        assert len(result["issues"]) > 0
        assert "suggested_patch" in result


# ------------------------------------------------------------------
# Engine integration
# ------------------------------------------------------------------


class TestEngineIntegration:
    def test_review_partimento_via_engine(self, tmp_path):
        engine = AlgorithmicPartimentoEngine()
        path = _write_chain_json(
            tmp_path,
            "p.json",
            {
                "key": "C major",
                "bassline": [["C3"], ["G2"], ["C3"]],
                "figures": [[["5", "3"]], [["5", "3"]], [["5", "3"]]],
                "cadences": ["measure 3: authentic cadence"],
            },
        )
        result = json.loads(engine.review_partimento(path))
        assert "message" in result

    def test_review_realization_via_engine(self, tmp_path):
        engine = AlgorithmicPartimentoEngine()
        path = _write_chain_json(
            tmp_path,
            "r.json",
            {
                "key": "C major",
                "soprano": [["E5"], ["D5"], ["E5"]],
                "alto": [["C4"], ["B3"], ["C4"]],
                "tenor": [["G3"], ["G3"], ["G3"]],
                "bass": [["C3"], ["G2"], ["C3"]],
            },
        )
        result = json.loads(engine.review_realized_score(path))
        assert "message" in result

    def test_full_pipeline_generate_realize_review(self, tmp_path):
        """End-to-end: generate -> realize -> review, all algorithmic."""
        from lib.utils.chain_utils import write_chain_json

        engine = AlgorithmicPartimentoEngine()

        # Generate
        partimento = engine.generate_partimento("4 bars in C major")

        # Write partimento JSON
        p_path = tmp_path / "partimento_01.json"
        write_chain_json(partimento, str(p_path), mode="generate-partimento")

        # Review partimento
        p_review = json.loads(engine.review_partimento(str(p_path)))
        assert "message" in p_review

        # Realize
        realized = engine.realize_partimento_satb(partimento)

        # Write realization JSON
        r_path = tmp_path / "realized_01.json"
        write_chain_json(realized, str(r_path), mode="realize-partimento")

        # Review realization
        r_review = json.loads(engine.review_realized_score(str(r_path)))
        assert "message" in r_review
