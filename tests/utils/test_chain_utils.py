from pathlib import Path
from types import SimpleNamespace

import pytest

from lib.utils.chain_utils import build_meta, is_likely_directory, resolve_output

# ------------------------------------------------------------------
# is_likely_directory
# ------------------------------------------------------------------


def test_is_likely_directory_true_for_no_extension():
    assert is_likely_directory("some/dir/path") is True
    assert is_likely_directory("/absolute/path/") is True  # trailing slash


def test_is_likely_directory_false_for_files():
    assert is_likely_directory("file.json") is False
    assert is_likely_directory("/tmp/file.musicxml") is False


# ------------------------------------------------------------------
# build_meta
# ------------------------------------------------------------------


def test_build_meta_contains_expected_fields():
    files = {"json": "foo.json", "midi": "foo.mid"}
    meta = build_meta("test‑mode", "dummy prompt", files)

    # Basic structural assertions
    assert meta["mode"] == "test‑mode"
    assert meta["prompt"] == "dummy prompt"
    assert meta["files"] == files
    # RFC‑3339 timestamp ends with Z
    assert meta["created_at"].endswith("Z")
    # UUID looks uuid‑y (5 parts separated by hyphens)
    assert len(meta["id"].split("-")) == 5


# ------------------------------------------------------------------
# resolve_output
# ------------------------------------------------------------------


def _make_args(output):
    """Return a dummy argparse‑like namespace with just an `output` attr."""
    return SimpleNamespace(output=str(output) if output else output)


def test_resolve_output_chain_dir(tmp_path: Path):
    """
    Passing a directory path should set is_chain=True and put *_01.json inside.
    """
    out_dir = tmp_path / "chain_dir"
    args = _make_args(out_dir)
    spec = resolve_output("partimento", args)

    assert spec.is_chain is True
    assert spec.chain_dir == out_dir
    assert spec.json == out_dir / "partimento_01.json"
    assert spec.xml == out_dir / "partimento.musicxml"
    assert spec.midi == out_dir / "partimento.mid"
    assert spec.ogg == out_dir / "partimento.ogg"


def test_resolve_output_flat_file(tmp_path: Path):
    """
    When no directory is supplied, resolve_output should create timestamped
    paths in 'generated/json' and is_chain should be False.
    """
    args = _make_args(None)
    spec = resolve_output("review", args)

    assert spec.is_chain is False
    # Should live in generated/json
    assert "generated/json" in str(spec.json)
    assert spec.json.suffix == ".json"
    # xml/midi/ogg path stems match
    assert spec.xml.with_suffix("").name == spec.json.with_suffix("").name
    assert spec.chain_dir is None
