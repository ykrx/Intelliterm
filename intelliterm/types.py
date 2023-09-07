from typing import Literal, TypedDict


AutoCopy = Literal['off', 'all', 'code']


class Colors(TypedDict):
    """Color definitions (for type hints).
    """
    info: str
    warning: str
    danger: str
    surface: str
    command: str
    arg: str
    option: str
    value: str
