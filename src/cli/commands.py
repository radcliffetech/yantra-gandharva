def register_lead_sheet(subparsers):
    parser = subparsers.add_parser(
        "lead-sheet", help="Generate MusicXML from a lead sheet JSON file"
    )
    parser.add_argument("input", help="Path to input JSON file")
    parser.add_argument(
        "output", nargs="?", help="Path to output MusicXML file (optional)"
    )


def register_generate_partimento(subparsers):
    parser = subparsers.add_parser(
        "generate-partimento", help="Use LLM to generate a partimento bassline"
    )
    parser.add_argument(
        "prompt", help="Natural language prompt describing the partimento to generate"
    )
    parser.add_argument(
        "--output", "-o", help="Path to save the generated JSON (optional)"
    )


def register_chain_partimento(subparsers):
    parser = subparsers.add_parser(
        "chain-partimento", help="Generate → Realize → Export a partimento"
    )
    parser.add_argument(
        "prompt", help="Natural language prompt to generate the partimento"
    )
    parser.add_argument(
        "--output", "-o", help="Optional output base filename (no extension)"
    )


def register_export_partimento_to_musicxml(subparsers):
    parser = subparsers.add_parser(
        "export-partimento-to-musicxml", help="Export partimento JSON to MusicXML"
    )
    parser.add_argument("input", help="Path to input JSON file")
    parser.add_argument(
        "output", nargs="?", help="Path to output MusicXML file (optional)"
    )


def register_realize_partimento(subparsers):
    parser = subparsers.add_parser(
        "realize-partimento", help="Realize a partimento into SATB texture"
    )
    parser.add_argument("input", help="Path to input partimento JSON file")
    parser.add_argument(
        "--output", "-o", help="Path to save the realized SATB JSON (optional)"
    )


def register_export_realized_partimento_to_musicxml(subparsers):
    parser = subparsers.add_parser(
        "export-realized-partimento-to-musicxml",
        help="Export realized partimento JSON to MusicXML",
    )
    parser.add_argument("input", help="Path to input realized partimento JSON file")
    parser.add_argument(
        "output", nargs="?", help="Path to output MusicXML file (optional)"
    )


def register_commands(subparsers):
    register_lead_sheet(subparsers)
    register_generate_partimento(subparsers)
    register_chain_partimento(subparsers)
    register_export_partimento_to_musicxml(subparsers)
    register_realize_partimento(subparsers)
    register_export_realized_partimento_to_musicxml(subparsers)
