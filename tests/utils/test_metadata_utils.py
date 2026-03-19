from lib.utils.metadata_utils import generate_metadata


def test_generate_metadata_has_required_fields():
    meta = generate_metadata("test prompt", "generate-partimento")
    assert meta["mode"] == "generate-partimento"
    assert meta["user_prompt"] == "test prompt"
    assert meta["source"] == "prompt"
    assert meta["version"] == "0.1.0"
    assert meta["created_at"].endswith("Z")
    assert len(meta["id"].split("-")) == 5


def test_generate_metadata_includes_system_prompt():
    meta = generate_metadata("prompt", "mode", system_prompt="sys prompt")
    assert meta["system_prompt"] == "sys prompt"


def test_generate_metadata_system_prompt_defaults_none():
    meta = generate_metadata("prompt", "mode")
    assert meta["system_prompt"] is None


def test_generate_metadata_timestamp_is_utc():
    meta = generate_metadata("p", "m")
    ts = meta["created_at"]
    # Should end with Z (UTC) and not contain +00:00
    assert ts.endswith("Z")
    assert "+00:00" not in ts
