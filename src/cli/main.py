import os
import sys

import argcomplete

# Ensure src/ is in sys.path for imports
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
import argparse
import logging

from colorama import Fore, init

logger = logging.getLogger(__name__)

from .commands import register_commands
from .handlers import handler_map

# For realize-figured-bass, import call_llm and realize_figured_bass_from_prompt directly

init(autoreset=True)


def main():
    parser = argparse.ArgumentParser(description="Yantra-Gandharva Score Generator")
    subparsers = parser.add_subparsers(dest="command")
    register_commands(subparsers)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.command in handler_map:
        handler_map[args.command](args)
    else:
        logger.warning(Fore.YELLOW + "Unknown or missing command.\n")
        parser.print_help()


if __name__ == "__main__":
    main()
