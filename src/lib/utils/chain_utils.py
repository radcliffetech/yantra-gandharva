import json
import logging
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from colorama import Fore, Style

logger = logging.getLogger(__name__)


@dataclass
class OutputSpec:
    json: Path
    xml: Path
    midi: Path
    ogg: Path
    chain_dir: Path | None
    is_chain: bool


def _timestamp() -> str:
    """Return a filesystem‑safe timestamp."""
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def is_likely_directory(path):
    """Return True if the path is probably a directory (no file extension)."""
    return not os.path.splitext(path)[1]


def get_next_versioned_filename(directory, base, ext=".json"):
    """
    Return next available versioned filename in directory, e.g. base_03.json.
    """

    files = list(Path(directory).glob(f"{base}_*.json"))
    numbers = [
        int(re.search(rf"{base}_(\d+)\{ext}", str(f)).group(1))
        for f in files
        if re.search(rf"{base}_(\d+)\{ext}", str(f))
    ]
    next_num = max(numbers, default=1) + 1
    return os.path.join(directory, f"{base}_{next_num:02}{ext}")


def write_chain_json(data, output_path, mode, source_path=None, prompt=None):
    """Write a JSON file with standard metadata + data block."""
    payload = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat() + "Z",
        "mode": mode,
        "source": source_path or "unknown",
        "user_prompt": prompt or None,
        "version": "0.1.0",
        "data": data,
    }
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2)


def write_metadata(directory, data):
    """Write metadata.json to the given directory."""
    with open(os.path.join(directory, "metadata.json"), "w") as f:
        json.dump(data, f, indent=2)


def log_step(msg, color=Fore.CYAN):
    logger.info(color + msg + Style.RESET_ALL)


def resolve_output(base_name: str, args) -> OutputSpec:
    """
    Decide whether we're writing into a chain directory (directory argument)
    or a flat set of files.  Returns an OutputSpec with fully‑qualified paths.
    """
    if args.output and is_likely_directory(args.output):
        chain = Path(args.output)
        chain.mkdir(parents=True, exist_ok=True)
        json_path = chain / f"{base_name}_01.json"
        xml_path = chain / f"{base_name}.musicxml"
        midi_path = chain / f"{base_name}.mid"
        ogg_path = chain / f"{base_name}.ogg"
        return OutputSpec(json_path, xml_path, midi_path, ogg_path, chain, True)

    # flat mode
    stem = Path(
        args.output or f"generated/json/{base_name}_{_timestamp()}"
    ).with_suffix("")
    stem.parent.mkdir(parents=True, exist_ok=True)
    return OutputSpec(
        json=stem.with_suffix(".json"),
        xml=stem.with_suffix(".musicxml"),
        midi=stem.with_suffix(".mid"),
        ogg=stem.with_suffix(".ogg"),
        chain_dir=None,
        is_chain=False,
    )


def build_meta(mode: str, prompt: str, files: dict[str, str]) -> dict:
    """Return a minimal metadata dict."""
    return {
        "id": str(uuid.uuid4()),
        # Use an explicit UTC timezone‑aware datetime and keep RFC‑3339 "Z" suffix
        "created_at": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "mode": mode,
        "prompt": prompt,
        "files": files,
        "version": "0.1.0",
    }


def pretty_summary(out: OutputSpec, iterations: int = 1) -> None:
    logger.info(Fore.GREEN + "\n📊 Summary:")
    logger.info(Fore.YELLOW + f"📄 Chain dir: {out.chain_dir or out.json.parent}")
    logger.info(Fore.YELLOW + f"📁 JSON: {out.json.name}")
    logger.info(Fore.YELLOW + f"🎧 Audio preview: {out.ogg.name}")
    logger.info(Fore.YELLOW + f"📝 Iterations: {iterations}")
    logger.info(Fore.CYAN + "\n🔗 Complete.")
