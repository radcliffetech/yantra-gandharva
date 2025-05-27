def register_commands(subparsers):
    # Chained command: realize and export figured bass
    chain_parser = subparsers.add_parser(
        "chain-figured-bass",
        help="Use LLM to realize a figured bass from a prompt and generate MusicXML",
    )
    chain_parser.add_argument("prompt", help="Prompt for figured bass realization")

    # LLM generation command
    gen_parser = subparsers.add_parser(
        "llm-generate", help="Generate score JSON using LLM"
    )
    gen_parser.add_argument(
        "type", choices=["jazz", "figured"], help="Score type to generate"
    )
    gen_parser.add_argument("prompt", help="Natural language prompt to feed the model")
    gen_parser.add_argument(
        "--output", "-o", help="Path to save the generated JSON (optional)"
    )

    # MusicXML generation command
    lead_parser = subparsers.add_parser(
        "lead-sheet", help="Generate MusicXML from a lead sheet JSON file"
    )
    lead_parser.add_argument("input", help="Path to input JSON file")
    lead_parser.add_argument(
        "output", nargs="?", help="Path to output MusicXML file (optional)"
    )

    # Figured bass MusicXML generation command
    fb_parser = subparsers.add_parser(
        "figured-bass", help="Generate MusicXML from a figured bass JSON file"
    )
    fb_parser.add_argument("input", help="Path to input JSON file")
    fb_parser.add_argument(
        "output", nargs="?", help="Path to output MusicXML file (optional)"
    )

    # LLM figured bass realization command
    rfb_parser = subparsers.add_parser(
        "realize-figured-bass", help="Use LLM to realize a figured bass from a prompt"
    )
    rfb_parser.add_argument(
        "prompt", help="Natural language prompt describing the figured bass progression"
    )
    rfb_parser.add_argument(
        "--output", "-o", help="Path to save the generated JSON (optional)"
    )
