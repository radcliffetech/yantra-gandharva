from .core import register_commands as register_core_commands
from .firebase import register_commands as register_firebase_commands
from .jazz import register_commands as register_jazz_commands
from .partimento import register_commands as register_partimento_commands


def register_commands(subparsers):
    register_core_commands(subparsers)
    register_partimento_commands(subparsers)
    register_jazz_commands(subparsers)
    register_firebase_commands(subparsers)
