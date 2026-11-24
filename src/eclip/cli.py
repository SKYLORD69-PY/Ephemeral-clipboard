import argparse
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eclip",
        description="Send a secret from one computer to another.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("send", help="Send the clipboard contents.")
    receive_parser = subparsers.add_parser("receive", help="Receive a secret.")
    receive_parser.add_argument("code", help="The short eclip code.")
    subparsers.add_parser("serve", help="Run the relay.")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    if args.command == "send":
        print("send: not implemented yet")
    elif args.command == "receive":
        print("receive: not implemented yet")
    elif args.command == "serve":
        print("serve: not implemented yet")


if __name__ == "__main__":
    main()
