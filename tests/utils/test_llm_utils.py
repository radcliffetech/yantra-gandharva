import importlib
import os

import pytest

openai = pytest.importorskip("openai", reason="openai package not installed")


def test_call_llm_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    import lib.utils.llm_utils as mod

    importlib.reload(mod)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        mod.call_llm("system", "user")


def test_default_model_reads_from_env(monkeypatch):
    monkeypatch.setenv("YANTRA_LLM_MODEL", "gpt-4-turbo")
    import lib.utils.llm_utils as mod

    importlib.reload(mod)
    assert mod.DEFAULT_MODEL == "gpt-4-turbo"
    # Reset
    monkeypatch.delenv("YANTRA_LLM_MODEL", raising=False)
    importlib.reload(mod)


def test_default_model_fallback(monkeypatch):
    monkeypatch.delenv("YANTRA_LLM_MODEL", raising=False)
    import lib.utils.llm_utils as mod

    importlib.reload(mod)
    assert mod.DEFAULT_MODEL == "gpt-4o"
