"""Tests for the engine abstraction layer."""

import argparse
import json

import pytest

from engines import EngineType
from engines.base import JazzEngine, PartimentoEngine
from genres.jazz.engines import get_jazz_engine
from genres.jazz.engines.algorithmic import AlgorithmicJazzEngine
from genres.jazz.engines.llm import LLMJazzEngine
from genres.partimento.engines import get_partimento_engine
from genres.partimento.engines.algorithmic import AlgorithmicPartimentoEngine
from genres.partimento.engines.llm import LLMPartimentoEngine


# ------------------------------------------------------------------
# EngineType enum
# ------------------------------------------------------------------


class TestEngineType:
    def test_llm_value(self):
        assert EngineType.LLM.value == "llm"

    def test_algorithmic_value(self):
        assert EngineType.ALGORITHMIC.value == "algorithmic"

    def test_from_string(self):
        assert EngineType("llm") == EngineType.LLM
        assert EngineType("algorithmic") == EngineType.ALGORITHMIC

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            EngineType("invalid")


# ------------------------------------------------------------------
# LLM engine wrappers delegate correctly
# ------------------------------------------------------------------


class TestLLMPartimentoEngine:
    def test_generate_delegates(self):
        calls = []

        def fake_llm(system, user):
            calls.append(("llm", system, user))
            return json.dumps({"title": "test", "key": "C", "bassline": ["C2"]})

        engine = LLMPartimentoEngine(fake_llm)
        result = engine.generate_partimento("test prompt")
        assert result["title"] == "test"
        assert len(calls) == 1

    def test_realize_delegates(self):
        calls = []

        def fake_llm(system, user):
            calls.append(("llm",))
            return json.dumps(
                {
                    "soprano": [["E5"]],
                    "alto": [["C4"]],
                    "tenor": [["G3"]],
                    "bass": [["C2"]],
                }
            )

        engine = LLMPartimentoEngine(fake_llm)
        result = engine.realize_partimento_satb({"key": "C", "bassline": ["C2"]})
        assert "soprano" in result
        assert len(calls) == 1

    def test_review_partimento_delegates(self, tmp_path):
        review_result = json.dumps({"message": "Looks good", "issues": []})

        def fake_llm(system, user):
            return review_result

        # Create a fake chain JSON file
        fake_json = tmp_path / "partimento.json"
        fake_json.write_text(
            json.dumps({"data": {"key": "C", "bassline": ["C2"]}})
        )

        engine = LLMPartimentoEngine(fake_llm)
        result = engine.review_partimento(str(fake_json))
        assert "Looks good" in result

    def test_review_realized_score_delegates(self, tmp_path):
        review_result = json.dumps({"message": "SATB OK", "issues": []})

        def fake_llm(system, user):
            return review_result

        fake_json = tmp_path / "realized.json"
        fake_json.write_text(
            json.dumps(
                {
                    "data": {
                        "soprano": [["E5"]],
                        "alto": [["C4"]],
                        "tenor": [["G3"]],
                        "bass": [["C2"]],
                    }
                }
            )
        )

        engine = LLMPartimentoEngine(fake_llm)
        result = engine.review_realized_score(str(fake_json))
        assert "SATB OK" in result


class TestLLMJazzEngine:
    def test_generate_delegates(self):
        calls = []

        def fake_llm(system, user):
            calls.append(("llm",))
            return json.dumps({"title": "Blues", "key": "F", "chords": ["Fmaj7"]})

        engine = LLMJazzEngine(fake_llm)
        result = engine.generate_jazz_lead_sheet("test prompt")
        assert result["title"] == "Blues"
        assert len(calls) == 1


# ------------------------------------------------------------------
# Engine factory dispatch
# ------------------------------------------------------------------


class TestGetPartimentoEngine:
    def test_llm_engine(self):
        fake_llm = lambda s, u: ""
        engine = get_partimento_engine(EngineType.LLM, call_llm=fake_llm)
        assert isinstance(engine, LLMPartimentoEngine)

    def test_algorithmic_engine(self):
        engine = get_partimento_engine(EngineType.ALGORITHMIC)
        assert isinstance(engine, AlgorithmicPartimentoEngine)


class TestGetJazzEngine:
    def test_llm_engine(self):
        fake_llm = lambda s, u: ""
        engine = get_jazz_engine(EngineType.LLM, call_llm=fake_llm)
        assert isinstance(engine, LLMJazzEngine)

    def test_algorithmic_engine(self):
        engine = get_jazz_engine(EngineType.ALGORITHMIC)
        assert isinstance(engine, AlgorithmicJazzEngine)


# ------------------------------------------------------------------
# Algorithmic engine stubs raise NotImplementedError
# ------------------------------------------------------------------


class TestAlgorithmicPartimentoStubs:
    def test_generate_is_implemented(self):
        engine = AlgorithmicPartimentoEngine()
        result = engine.generate_partimento("8 bars in C major")
        assert "bassline" in result

    def test_realize_is_implemented(self):
        engine = AlgorithmicPartimentoEngine()
        data = {
            "key": "C major",
            "bassline": [["C3"], ["G2"], ["C3"]],
            "figures": [[["5", "3"]], [["5", "3"]], [["5", "3"]]],
        }
        result = engine.realize_partimento_satb(data)
        assert "soprano" in result

    def test_review_partimento_is_implemented(self, tmp_path):
        import json

        engine = AlgorithmicPartimentoEngine()
        path = tmp_path / "p.json"
        path.write_text(
            json.dumps(
                {
                    "data": {
                        "key": "C major",
                        "bassline": [["C3"], ["G2"], ["C3"]],
                        "figures": [[["5", "3"]], [["5", "3"]], [["5", "3"]]],
                        "cadences": ["measure 3: authentic cadence"],
                    }
                }
            )
        )
        result = json.loads(engine.review_partimento(str(path)))
        assert "message" in result

    def test_review_realized_is_implemented(self, tmp_path):
        import json

        engine = AlgorithmicPartimentoEngine()
        path = tmp_path / "r.json"
        path.write_text(
            json.dumps(
                {
                    "data": {
                        "key": "C major",
                        "soprano": [["E5"]],
                        "alto": [["G4"]],
                        "tenor": [["C4"]],
                        "bass": [["C3"]],
                    }
                }
            )
        )
        result = json.loads(engine.review_realized_score(str(path)))
        assert "message" in result


class TestAlgorithmicJazzEngine:
    def test_generate_is_implemented(self):
        engine = AlgorithmicJazzEngine()
        result = engine.generate_jazz_lead_sheet("blues in C")
        assert "chords" in result
        assert len(result["chords"]) == 12


# ------------------------------------------------------------------
# CLI --engine flag parsing
# ------------------------------------------------------------------


class TestEngineCliFlag:
    def _make_parser(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        from cli.commands.partimento import register_generate_partimento

        register_generate_partimento(subparsers)
        return parser

    def test_default_is_llm(self):
        parser = self._make_parser()
        args = parser.parse_args(["generate-partimento", "test prompt"])
        assert args.engine == "llm"

    def test_explicit_llm(self):
        parser = self._make_parser()
        args = parser.parse_args(
            ["generate-partimento", "test prompt", "--engine", "llm"]
        )
        assert args.engine == "llm"

    def test_explicit_algorithmic(self):
        parser = self._make_parser()
        args = parser.parse_args(
            ["generate-partimento", "test prompt", "--engine", "algorithmic"]
        )
        assert args.engine == "algorithmic"

    def test_invalid_engine_rejected(self):
        parser = self._make_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(
                ["generate-partimento", "test prompt", "--engine", "invalid"]
            )


# ------------------------------------------------------------------
# Handler engine resolution
# ------------------------------------------------------------------


class TestEngineResolutionFromArgs:
    """Test the engine dispatch logic as used by handlers.

    We test through get_partimento_engine + EngineType directly,
    since importing cli.handlers triggers firebase (optional dep).
    This tests the same logic that _engine_from_args uses.
    """

    def test_default_llm(self):
        engine_type = EngineType(getattr(argparse.Namespace(), "engine", "llm"))
        engine = get_partimento_engine(engine_type, call_llm=lambda s, u: "")
        assert isinstance(engine, LLMPartimentoEngine)

    def test_algorithmic(self):
        engine_type = EngineType(
            getattr(argparse.Namespace(engine="algorithmic"), "engine", "llm")
        )
        engine = get_partimento_engine(engine_type)
        assert isinstance(engine, AlgorithmicPartimentoEngine)

    def test_explicit_llm(self):
        engine_type = EngineType(
            getattr(argparse.Namespace(engine="llm"), "engine", "llm")
        )
        engine = get_partimento_engine(engine_type, call_llm=lambda s, u: "")
        assert isinstance(engine, LLMPartimentoEngine)
