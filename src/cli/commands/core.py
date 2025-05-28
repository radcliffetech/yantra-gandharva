def register_write_audio(subparsers):
    parser = subparsers.add_parser(
        "export-audio", help="Conver MIDI file to ogg using timidity"
    )
    parser.add_argument("input", help="Path to the .mid file")


def register_inspect_musicxml(subparsers):
    parser = subparsers.add_parser(
        "inspect-musicxml", help="Print summary of a MusicXML file"
    )
    parser.add_argument("input", help="Path to .musicxml file to inspect")


def register_describe_chain(subparsers):
    parser = subparsers.add_parser(
        "describe-chain", help="Describe the chain of operations for a partimento"
    )
    parser.add_argument("input", help="Path to the partimento JSON file")
    parser.add_argument(
        "--output", "-o", help="Path to save the description (optional)"
    )


def register_commands(subparsers):
    register_describe_chain(subparsers)
    register_inspect_musicxml(subparsers)
    register_write_audio(subparsers)
