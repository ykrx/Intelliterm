import argparse
import logging
import os
import sys
from typing import NoReturn, Optional

from intelliterm import __version__
from intelliterm.chat import Chat
from intelliterm.console import console
from intelliterm.prompt import SPECIAL_PROMPTS, Prompt
from intelliterm.utils import (
    intelliterm,
    is_git_diff,
    logger,
    setup_dirs,
    setup_logging,
)


__author__ = "Yulian Kraynyak"
__copyright__ = "Yulian Kraynyak"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


class ArgParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        console.print(f"{intelliterm.__name__}: {message}\n")

        if "file" in message:
            self.print_file_usage()
        else:
            self.print_usage()
        self.exit(2)

    def print_file_usage(self) -> None:
        console.print(
            f"usage: [green]{self.prog}",
            "[reset]-f/--file",
            "[arg]<path>[reset]",
        )

    @staticmethod
    def validate_file(path: str) -> str:
        if not os.path.isfile(path):
            raise argparse.ArgumentTypeError(f"[danger]{path} [reset]is not a file")
        else:
            return path


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse command line parameters.
    
    Args:
        args (list[str]): CLI parameters as list of strings (for example  `["--help"]`).
            
    Returns:
        argparse.Namespace: CLI parameters namespace.
    """
    parser = ArgParser()
    parser.add_argument(
        "-v",
        "-V",
        "--version",
        action="version",
        help="show version number",
        version=__version__,
    )
    parser.add_argument(
        dest="prompt",
        help="prompt",
        nargs="*",
        type=str,
        metavar="STR",
    )
    parser.add_argument(     # TODO(unfinished)
        "-f",
        "--file",
        dest="file",
        help="input a file",
        type=ArgParser.validate_file,
    )
    parser.add_argument(
        "-m",
        "--mini",
        "--oneshot",
        dest="oneshot",
        action="store_true",
        default=False,
        help=f"complete prompt without entering {intelliterm.__name__}",
    )
    parser.add_argument(
        "-c",
        "--copy",
        dest="autocopy",
        action="store",
        choices=("off", "all", "code"),
        const="all",
        default="off",
        nargs="?",
        help="autocopy response to clipboard",
    )

    return parser.parse_args(args)


def main(_args: list[str]) -> None:
    setup_dirs()
    setup_logging()

    logger.info(f"Starting {intelliterm.__name__}")

    args = parse_args(_args)
    chat = Chat(oneshot=args.oneshot, autocopy=args.autocopy)

    if sys.stdin.isatty():
        # is NOT stdin
        prompt: Optional[Prompt] = None

        if args.prompt:
            # $ ai <prompt>
            prompt = Prompt(content=" ".join(args.prompt))

        if args.file:
            # $ ai -f/--file <file>
            with open(args.file, "r") as file:
                prompt = Prompt(
                    content=file.read() + prompt.content if prompt else "",
                    is_file=True,
                )
                _logger.error(f"Inputting file {args.file}")

        if prompt is None or len(prompt.content.strip()) == 0:
            # $ ai
            console.clear()
            chat.listen()
        else:
            chat.ask(prompt)
    else:
        # <stdin> | ai
        # Call model to complete prompt from stdin
        if args.prompt:
            prompt = Prompt(content=" ".join(args.prompt) + sys.stdin.read().strip())
            chat.ask(prompt)
        else:
            prompt = Prompt(content=sys.stdin.read().strip())

            if len(prompt.content) > 0:
                if is_git_diff(prompt.content):
                    prompt.content = SPECIAL_PROMPTS['GIT_DIFF'] + prompt.content
                chat.oneshot(True)
                chat.ask(prompt)
            else:
                console.error("Empty input")


def run() -> None:
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
