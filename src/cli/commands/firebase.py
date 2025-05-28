def register_list_realizations(subparsers):
    parser = subparsers.add_parser(
        "list-realizations", help="List all realization documents in Firebase"
    )


def register_push_chain(subparsers):
    parser = subparsers.add_parser(
        "push-chain", help="Upload a realization chain folder to Firebase"
    )
    parser.add_argument("input", help="Path to a chain folder containing metadata.json")


def register_commands(subparsers):
    register_push_chain(subparsers)
    register_list_realizations(subparsers)
