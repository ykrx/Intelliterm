import os
import re
from typing import Any, Mapping, Optional, cast

from rich.console import Console as C
from rich.style import StyleType
from rich.theme import Theme

from intelliterm.styling import COLORS, DANGER_STYLE, INFO_STYLE, WARNING_STYLE


class Console(C):
    """A class for printing formatted messages to the console.

    Inherits from rich.console's `Console`.

    Methods:
        info(*objects: Any) -> None:
            Prints the given objects to the console as information.
        warning(*objects: Any) -> None: 
            Prints the given objects to the console as a warning.
        error(*objects: Any) -> None: 
            Prints the given objects to the console as an error.
        divider(*objects: Any) -> None:  
            Prints a divider as wide as the terminal window.
    """
    def info(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        """Print to console as info.
        """
        message = " ".join(str(o) for o in objects)
        self.print(
            f"[bold blue]i [info][not bold]{message}",
            style=INFO_STYLE,
        )

    def warning(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        """Print to console as warning.
        """
        message = " ".join(str(o) for o in objects)
        self.print(
            f":warning: {message}",
            sep=sep,
            end=end,
            style=WARNING_STYLE,
        )

    def error(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        """Print to console as error.
        """
        message = " ".join(str(o) for o in objects)
        self.print(
            f":warning: {message}",
            sep=sep,
            end=end,
            style=DANGER_STYLE,
        )

    def with_divider(self, title: Optional[str] = None) -> None:
        """Print a divider as wide as the terminal window.
        
        Args:
            title (Optional[str]): Title to center in divider. Defaults to None.
        """
        if title:
            has_emoji = re.search(r":\w+:", title)
            emoji_offset = len(has_emoji.group()) if has_emoji else 0
            offset = (len(title) - emoji_offset + 2) // 2

            self.print(
                (f"[black]{title} " + "-" * (os.get_terminal_size().columns - len(title))),
            )
        else:
            self.print('-' * os.get_terminal_size().columns)


console = Console(theme=Theme(cast(Mapping[str, StyleType] | None, COLORS)))
