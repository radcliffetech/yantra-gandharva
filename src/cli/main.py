import os
import sys

# Ensure src/ is in sys.path for imports
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
import argparse

from colorama import Fore, Style, init

from . import handlers
from .commands import register_commands

# For realize-figured-bass, import call_llm and realize_figured_bass_from_prompt directly

init(autoreset=True)


def main():
    parser = argparse.ArgumentParser(description="Yantra-Gandharva Score Generator")
    subparsers = parser.add_subparsers(dest="command")
    register_commands(subparsers)

    args = parser.parse_args()

    handler_map = {
        "llm-generate": handlers.handle_llm_generate,
        "lead-sheet": handlers.handle_generate_lead_sheet,
        "figured-bass": handlers.handle_generate_figured_bass,
        "realize-figured-bass": handlers.handle_realize_figured_bass,
        "chain-figured-bass": handlers.handle_chain_figured_bass,
    }

    if args.command in handler_map:
        handler_map[args.command](args)
    else:
        print(Fore.YELLOW + "Unknown or missing command.\n")
        parser.print_help()


if __name__ == "__main__":
    main()
