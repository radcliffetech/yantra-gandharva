def register_lead_sheet(subparsers):
    parser = subparsers.add_parser(
        "lead-sheet", help="Generate MusicXML from a lead sheet JSON file"
    )
    parser.add_argument("input", help="Path to input JSON file")
    parser.add_argument(
        "output", nargs="?", help="Path to output MusicXML file (optional)"
    )


def register_generate_lead_sheet(subparsers):
    parser = subparsers.add_parser(
        "generate-lead-sheet",
        help="Generate a jazz lead sheet from a prompt",
    )
    parser.add_argument(
        "prompt", help="Natural language prompt (e.g. '12-bar blues in F')"
    )
    parser.add_argument(
        "--output", "-o", help="Path to save the generated JSON (optional)"
    )
    parser.add_argument(
        "--engine",
        choices=["llm", "algorithmic"],
        default="llm",
        help="Engine to use: 'llm' (default) or 'algorithmic' (template-based)",
    )


def register_commands(subparsers):
    register_lead_sheet(subparsers)
    register_generate_lead_sheet(subparsers)
