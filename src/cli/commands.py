def register_generate_and_review_partimento(subparsers):
    parser = subparsers.add_parser(
        "generate-and-review-partimento",
        help="Generate a partimento, review it, and export to MusicXML (no realization)",
    )
    parser.add_argument(
        "prompt", help="Natural language prompt describing the partimento to generate"
    )
    parser.add_argument(
        "--output", "-o", help="Path to save the generated JSON (optional)"
    )


def register_review_score(subparsers):
    parser = subparsers.add_parser(
        "review-score", help="Use LLM to review a realized SATB partimento"
    )
    parser.add_argument("input", help="Path to the realized SATB JSON file")


def register_revise_score(subparsers):
    parser = subparsers.add_parser(
        "revise-score", help="Apply a patch to a realized partimento"
    )
    parser.add_argument("input", help="Path to the realized SATB JSON file")
    parser.add_argument(
        "patch", help="Path to the JSON review file with suggested_patch"
    )
    parser.add_argument("--output", "-o", help="Path to save the revised JSON")


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


def register_inspect_musicxml(subparsers):
    parser = subparsers.add_parser(
        "inspect-musicxml", help="Print summary of a MusicXML file"
    )
    parser.add_argument("input", help="Path to .musicxml file to inspect")


def register_review_partimento(subparsers):
    parser = subparsers.add_parser(
        "review-partimento", help="Use LLM to review a partimento structure"
    )
    parser.add_argument("input", help="Path to the partimento JSON file")


def register_commands(subparsers):
    register_lead_sheet(subparsers)
    register_generate_partimento(subparsers)
    register_chain_partimento(subparsers)
    register_export_partimento_to_musicxml(subparsers)
    register_realize_partimento(subparsers)
    register_export_realized_partimento_to_musicxml(subparsers)
    register_inspect_musicxml(subparsers)
    register_review_score(subparsers)
    register_revise_score(subparsers)
    register_review_partimento(subparsers)
    register_generate_and_review_partimento(subparsers)
