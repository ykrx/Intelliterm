import datetime
import logging
import os
import re
from typing import Literal, TypedDict

import platformdirs

import intelliterm

# setup_cfg_path = Path(__file__).parent.joinpath("setup.cfg")
# app_config = c(setup_cfg_path)

AutoCopy = Literal["off", "all", "code"]

CODE_THEME = "lightbulb"

APP_AUTHOR = "Yulian Kraynyak"
USER_DATA_DIR = platformdirs.user_data_dir(intelliterm.__name__, APP_AUTHOR)
DOCUMENTS_DIR = platformdirs.user_documents_dir()
SAVED_CHATS_DIR = os.path.join(DOCUMENTS_DIR, intelliterm.__name__, "chats")
LOGS_DIR = os.path.join(DOCUMENTS_DIR, intelliterm.__name__, "logs")

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


class Colors(TypedDict):
    """Color definitions (for type hints).
    """
    info: str
    warning: str
    danger: str
    primary: str
    secondary: str
    surface: str
    command: str
    arg: str
    option: str
    value: str


COLORS: Colors = {
    "info": "bright_black",
    "warning": "yellow",
    "danger": "red",
    "primary": "#ffd173",
    "secondary": "yellow",
    "surface": "#121722",
    "command": "bold green",
    "arg": "not bold blue",
    "option": "not bold magenta",
    "value": "green"
}

TIPS = {
    "config": [
        "[bold]tip:[not bold] " + tip for tip in [
            "switch to other configs with [command]!use [arg]<name>",
            "add/edit configs with [command]!config [option]edit",
        ]
    ]
}


def setup_logging() -> None:
    """Setup logging.
    """
    log_format = (
        "[%(asctime)s] %(levelname)s:%(name)s.%(module)s:%(funcName)s: " + "%(message)s"
    )
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(LOGS_DIR, f"{intelliterm.__name__}_logs_{timestamp}.log")
    logging.basicConfig(
        level=logging.INFO,
        filename=filename,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


logger = logging.getLogger(intelliterm.__name__)


def pretty_dict(dict: dict, colors: bool = True) -> str:
    """Prettify dictionary.
       
        Args:
            dict (dict): Dictionary object.
            colors (bool): Use colors. Defaults to True.
            
        Returns:
            str: Formatted string.
       """
    o = ""
    for i, (k, v) in enumerate(dict.items()):
        is_last = i == len(dict) - 1
        o += f"{k}[reset]: "
        o += "[value]" if colors else ""
        o += v + "[reset]"
        if not is_last:
            o += "\n"
    return o


def longest_line(s: str) -> int:
    """Utility to get length of longest line in string.
    """
    s = re.sub(r"\[.*?]", "", s)     # strip formatting tags
    return max(len(line) for line in s.split("\n"))


def get_file_info(path: str) -> dict[str, str]:
    """Get file information for file at path.
    
    Args:
        path (str): Path to file.
            
    Returns:
        dict[str, str]: Dictionary containing file info.
    """
    return {
        "path": path,
        "type": os.path.splitext(path)[1][1:].lower(),
    }


def is_git_diff(content: str) -> bool:
    """Check if content of string is a git diff.
    """
    return content.startswith("diff --git")


def setup_dirs() -> None:
    os.makedirs(SAVED_CHATS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
