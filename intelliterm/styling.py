from rich.style import Style

from intelliterm.types import Colors

ANSI_COLORS = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[33m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'reset': '\033[0m'
}

COLORS: Colors = {
    "info": "blue",
    "warning": "yellow",
    "danger": "red",
    "surface": "#121722",
    "command": "blue bold ",
    "arg": "magenta not bold",
    "option": "magenta not bold",
    "value": "magenta not bold "
}

INFO_STYLE = Style(color=f"{COLORS['info']}")
WARNING_STYLE = Style(color=f"{COLORS['danger']}")
DANGER_STYLE = Style(color=f"{COLORS['danger']}", bold=True)
