def register_chain_partimento_realization(subparsers):
    parser = subparsers.add_parser(
        "chain-partimento-realization", help="Generate → Realize → Export a partimento"
    )
    parser.add_argument(
        "prompt", help="Natural language prompt to generate the partimento"
    )
    parser.add_argument(
        "--output", "-o", help="Optional output base filename (no extension)"
    )
    parser.add_argument(
        "--iterations", type=int, default=1, help="Number of realization review loops"
    )


def register_chain_partimento_only(subparsers):
    parser = subparsers.add_parser(
        "chain-partimento-only",
        help="Generate a partimento, review it, and export to MusicXML (no realization)",
    )
    parser.add_argument(
        "prompt", help="Natural language prompt describing the partimento to generate"
    )
    parser.add_argument(
        "--output", "-o", help="Path to save the generated JSON (optional)"
    )
    parser.add_argument(
        "--iterations", type=int, default=1, help="Number of realization review loops"
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


def register_realize_partimento(subparsers):
    parser = subparsers.add_parser(
        "realize-partimento", help="Realize a partimento into SATB texture"
    )
    parser.add_argument("input", help="Path to input partimento JSON file")
    parser.add_argument(
        "--output", "-o", help="Path to save the realized SATB JSON (optional)"
    )


def register_review_partimento(subparsers):
    parser = subparsers.add_parser(
        "review-partimento", help="Use LLM to review a partimento structure"
    )
    parser.add_argument("input", help="Path to the partimento JSON file")
    parser.add_argument(
        "--output", "-o", help="Path to save the generated JSON (optional)"
    )


def register_review_realization(subparsers):
    parser = subparsers.add_parser(
        "review-realization", help="Use LLM to review a realized SATB partimento"
    )
    parser.add_argument("input", help="Path to the realized SATB JSON file")
    parser.add_argument(
        "--output", "-o", help="Path to save the generated JSON (optional)"
    )


def register_revise_partimento(subparsers):
    parser = subparsers.add_parser(
        "revise-partimento", help="Apply a patch to a partimento structure"
    )
    parser.add_argument("input", help="Path to the partimento JSON file")
    parser.add_argument(
        "patch", help="Path to the JSON review file with suggested_patch"
    )
    parser.add_argument("--output", "-o", help="Path to save the revised JSON")


def register_revise_realization(subparsers):
    parser = subparsers.add_parser(
        "revise-realization", help="Apply a patch to a realized partimento"
    )
    parser.add_argument("input", help="Path to the realized SATB JSON file")
    parser.add_argument(
        "patch", help="Path to the JSON review file with suggested_patch"
    )
    parser.add_argument("--output", "-o", help="Path to save the revised JSON")


def register_export_partimento_to_musicxml(subparsers):
    parser = subparsers.add_parser("export-partimento", help="Export partimento JSON")
    parser.add_argument("input", help="Path to input JSON file")
    parser.add_argument(
        "output", nargs="?", help="Path to output MusicXML file (optional)"
    )


def register_export_realized_partimento_to_musicxml(subparsers):
    parser = subparsers.add_parser(
        "export-realization",
        help="Export realized partimento JSON",
    )
    parser.add_argument("input", help="Path to input realized partimento JSON file")
    parser.add_argument(
        "output", nargs="?", help="Path to output MusicXML file (optional)"
    )


def register_commands(subparsers):
    # full chains
    register_chain_partimento_realization(subparsers)
    register_chain_partimento_only(subparsers)

    # generate
    register_generate_partimento(subparsers)
    register_realize_partimento(subparsers)

    # review
    register_review_partimento(subparsers)
    register_review_realization(subparsers)

    # revise
    register_revise_partimento(subparsers)
    register_revise_realization(subparsers)

    # export
    register_export_partimento_to_musicxml(subparsers)
    register_export_realized_partimento_to_musicxml(subparsers)
