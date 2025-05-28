def register_lead_sheet(subparsers):
    parser = subparsers.add_parser(
        "lead-sheet", help="Generate MusicXML from a lead sheet JSON file"
    )
    parser.add_argument("input", help="Path to input JSON file")
    parser.add_argument(
        "output", nargs="?", help="Path to output MusicXML file (optional)"
    )


def register_commands(subparsers):
    register_lead_sheet(subparsers)
