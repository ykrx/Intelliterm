import os
import re
from typing import Any, Generator, Optional

from prompt_toolkit import HTML, PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator
from rich.columns import Columns
from rich.panel import Panel

import intelliterm
from intelliterm.console import console
from intelliterm.notifications import notification

key_bindings = KeyBindings()


# TODO(implement): add useful bindings
@key_bindings.add("escape", "c")     # option + c
def exit_(event: Any) -> None:
    """
        Pressing Ctrl-d will exit the user interface.
        """
    event.app.exit()


# TODO(possibly): persist prompt history across sessions
def get_history() -> None:
    pass


session: PromptSession = PromptSession()     #history=)


def bottom_toolbar() -> Any:
    from intelliterm.config import config

    buffer = session.default_buffer
    input = buffer.text
    curr_index = input.count(" ")
    alias, *args = input.split(" ")

    output = ""

    if not notification.read:
        output = notification.message
    else:
        output = f"<strong>{config.active().name}</strong>"

        if input == CommandPalette.TRIGGER:
            output = "Enter a command"
        if CommandPalette.is_valid_input(input):
            command = CommandPalette.get_command(alias)

            if command:
                output = alias + " "

                if command.args:
                    output += " | ".join(
                        arg.name if arg.is_option else f"&lt;{arg.name}&gt;"
                        for arg in command.args
                    )
            if output.startswith(CommandPalette.TRIGGER):
                output_groups = output.split(" ", 1)

                try:
                    output_groups[curr_index
                                  ] = f"<strong>{output_groups[curr_index]}</strong>"
                    output = " ".join(output_groups)
                except IndexError:
                    pass
        else:
            if input != CommandPalette.TRIGGER:
                output = f"Unknown command: <strong><style color='ansired'>{input.strip()}</style></strong>"
    return HTML(output)


def rprompt() -> str:
    from intelliterm.config import config
    return f"[{config.active().name}]"


def prompt() -> str:
    """Prompt for user input.
    
    Returns:
        str: User input.
    """
    from intelliterm.config import config

    style: Style = Style.from_dict({
        "": "",
        "caret": f"fg:ansi{config.get('accent_color')}",
        "bottom-toolbar": "fg:ansiblack bg:black",
    })

    return session.prompt(
        message=[
            ("class:caret", ">"),
            ("class:input", " "),
        ],
        auto_suggest=AutoSuggestFromHistory(),
        completer=FuzzyCompleter(CommandCompleter()),
        mouse_support=False,
        key_bindings=key_bindings,
        validator=validator,
        validate_while_typing=False,
        bottom_toolbar=bottom_toolbar,
        placeholder=HTML(f"<ansiblack>  ({config.active().name})</ansiblack>"),
     # rprompt=rprompt,
        style=style,
    )


class CommandArgument:
    """Class defining a command argument/option.
    
    Attributes:
        name (str): Argument name.
        pos (Optional[int]): Argument position.
        is_option (bool): Argument is an option for a command. Defaults to False.
            (ex: "edit" in: !config edit)
    
    """

    # TODO(refactor): remove `is_option` (ie: improve logic separation)
    def __init__(
        self,
        name: str,
        pos: Optional[int] = None,
        is_option: bool = False,
    ) -> None:
        self.name = name
        self.pos = pos
        self.is_option = is_option


class CommandExample:
    """Class defining a command usage CommandExample.
    
    Attributes:
        command (str): Command name.
        args (Optional[list[Argument]]): List of command arguments/options.
    """
    def __init__(self, command: str, args: Optional[list[CommandArgument]]) -> None:
        self.command = command
        self.args = args


class CommandUsage:
    """Class defining a usage CommandExample for a `Command`.
    
    Attributes:
        command (str): Command name.
        description (str): Usage description.
        args (list[Argument]): List of arguments. Defaults to empty list.
        examples (list[CommandExample]): List of examples. Defaults to empty list.
        
    Methods:
        hint() -> str:
            Returns a helpful hint explaining how to use a command.
    """
    def __init__(
        self,
        command: str,
        description: str,
        args: list[CommandArgument] = [],
        examples: list[CommandExample] = [],
    ):
        self.command = command
        self.args = args
        self.description = description
        self.examples = examples

    def hint(self) -> str:
        """Returns a helpful hint explaining how to use a command.
        
        Returns:
            str
        """
        hint = f"[command]{CommandPalette.TRIGGER}{self.command}[reset]"

        for arg in self.args:
            hint += (
                f" [option]{arg.name}[reset]"
                if arg.is_option else f" [arg]<{arg.name}>[reset]"
            )
        hint += f"\n\t\t{self.description}\n"

        if self.examples:
            hint += "\t\t[bold italic]example:[reset] "

            for example in self.examples:
                hint += f"[command]{CommandPalette.TRIGGER + self.command}[reset]"

                if example.args:
                    for arg in example.args:
                        hint += f"[arg] {arg.name}"
        hint += "[reset]\n\n"
        return hint


class Command:
    """Class defining a CommandPalette command.
    
    Attributes:
        name (str): Command name.
        description (str): Command description.
        aliases (list[str]): Command aliases.
        args (Optional[list[Argument]]): Command arguments. Defaults to None.
        usage (Optional[list[Usage]]): Command usage template. Defaults to None.
            
    Methods:
        hint() -> str:
            Return documentation hint (command options, usage and examples).
    """
    def __init__(
        self,
        name: str,
        description: str,
        aliases: list[str],
        args: Optional[list[CommandArgument]] = None,
        usage: Optional[list[CommandUsage]] = None,
    ) -> None:
        self.name = name
        self.description = description
        self.aliases = aliases
        self.args = args
        self.usage = usage

    def hint(self) -> str:
        """Return documentation hint (command options, usage and examples).
        
        Returns: 
            str
        """
        hint = ""

        if self.args:
            args = [a for a in self.args if not a.is_option]
            options = [a for a in self.args if a.is_option]

            if args:
                hint += "  [bold italic]args:[reset]\n"
                hint += "\n".join(f"\t[arg]<{arg.name}>[reset]" for arg in args) + "\n"
            if options:
                hint += "  [bold italic]options:[reset]\n"
                hint += "\n".join(
                    f"\t[option]{option.name}[reset]" for option in options
                ) + "\n"
        if self.usage:
            hint += "  [bold italic]usage:[reset]\n\t"
            hint += "\t".join(u.hint() for u in self.usage)

        return hint


class CommandPalette:
    """Class representing a command manager that handles intelliterm-specific commands.
    
    Methods:
        get_command(alias: str) -> Optional[Command]:
            Get command matching alias.  
        help() -> None:
            Show available commands and how to use them.
        is_command(input: str) -> bool:
            Utility to check if input starts with the command trigger.
        is_valid_input(input: str) -> bool:
            Check if input matches a valid command alias.
        is_secondary_alias(alias: str) -> bool:
            Check if alias is not a primary alias 
            (ie: is shortened variant, like `h` for `help`).
        unrecognized(alias: str) -> None:
            Handle unrecognized command alias.
    """
    TRIGGER: str = "!"
    COMMAND_REGEX = r"^!(\w+)(?:\s{0,1}(.*))?"

    AVAILABLE_COMMANDS: list[Command] = [
        Command(
            name="help",
            description="Show available commands",
            aliases=["h", "help"],
        ),
        Command(
            name="version",
            description="Show version",
            aliases=["v", "version"],
        ),
        Command(
            name="config",
            description=f"Manage {intelliterm.__name__} configurations",
            args=[
                CommandArgument("name"),
                CommandArgument("edit", is_option=True),
                CommandArgument("reset", is_option=True),
            ],
            aliases=["u", "use", "cfg", "switch", "config"],
            usage=[
                CommandUsage(
                    command="config",
                    description="Show active configuration",
                ),
                CommandUsage(
                    command="use",
                    args=[CommandArgument("name")],
                    description=
                    "[reset]Use / switch to another configuration (case-insensitive)",
                    examples=[
                        CommandExample(command="use", args=[CommandArgument("gpt3")])
                    ],
                ),
                CommandUsage(
                    command="config",
                    args=[CommandArgument("edit", is_option=True)],
                    description=(
                        "Edit configurations file " +
                        f"(via {os.environ.get('EDITOR', 'nano')})"
                    )
                ),
                CommandUsage(
                    command="config",
                    args=[CommandArgument("reset", is_option=True)],
                    description="Reset configuration to defaults"
                ),
            ],
        ),
        Command(
            name="info",
            description="Show chat info",
            aliases=["i", "info"],
        ),
        Command(
            name="new",
            description="Start new chat / clear context",
            aliases=["n", "new"],
        ),
        Command(
            name="save",
            description="Save chat",
            aliases=["s", "save"],
        ),
        Command(
            name="load",
            description="Load chat",
            aliases=["l", "load"],
        ),
        Command(
            name="copy",
            description="Copy response",
            aliases=["c", "copy"],
            args=[CommandArgument("code", is_option=True)]
        ),
        Command(
            name="run",
            description="Run code block in response",
            aliases=["r", "run"],
        ),
        Command(
            name="file",
            description="Input a file",
            aliases=["f", "file"],
            args=[
                CommandArgument("path"),
                CommandArgument("prompt"),
            ],
            usage=[
                CommandUsage(
                    command="file",
                    args=[
                        CommandArgument("path"),
                        CommandArgument("prompt"),
                    ],
                    description="Input file with prompt",
                    examples=[
                        CommandExample(
                            command="file",
                            args=[
                                CommandArgument("file.txt"),
                                CommandArgument("explain this file"),
                            ]
                        )
                    ]
                ),
            ],
        ),
        Command(
            name="shell",
            description="Run a shell command",
            aliases=["os", "shell"],
            args=[CommandArgument("command")],
            usage=[
                CommandUsage(
                    command="shell",
                    args=[CommandArgument("command")],
                    description=
                    f"Run basic shell commands within {intelliterm.__name__}",
                    examples=[
                        CommandExample(command="shell", args=[CommandArgument("ls")])
                    ]
                ),
            ],
        ),
        Command(
            name="quit",
            description=f"Quit {intelliterm.__name__}",
            aliases=["q", "quit"],
        )
    ]

    GROUPED_ALIASES = [command.aliases for command in AVAILABLE_COMMANDS]
    PRIMARY_ALIASES = [
        command.name if command.name in command.aliases else command.aliases[0]
        for command in AVAILABLE_COMMANDS
    ]
    ALL_ALIASES = [alias for command in AVAILABLE_COMMANDS for alias in command.aliases]

    @staticmethod
    def get_command(alias: str) -> Optional[Command]:
        """Get command matching alias.
        
        Args: 
            alias (str): Command alias.
            
        Returns:
            Optional(Command): Command if it exists, otherwise None.
        """
        alias = alias.replace(CommandPalette.TRIGGER, "")
        return next(
            (
                command for command in CommandPalette.AVAILABLE_COMMANDS
                if alias in command.aliases
            ),
            None,
        )

    @staticmethod
    def get_aliases(command_name: str) -> list[str]:
        """Get all aliases for command with name.
        
        Args:
            command_name (str): Command name.
            
        Returns:
            list[str]: List of aliases associated with command.
        """
        aliases = []
        command = CommandPalette.get_command(command_name)

        if command:
            aliases = command.aliases
        return aliases

    @staticmethod
    def help() -> None:
        """Show available commands and how to use them.
        """
        help_message = ""

        for i, command in enumerate(CommandPalette.AVAILABLE_COMMANDS):
            aliases = [CommandPalette.TRIGGER + alias for alias in command.aliases]
            help_message += f"[command]{', '.join(aliases)}"
            help_message += f"[reset] : {command.description}"
            help_message += "\n" if i != len(
                CommandPalette.AVAILABLE_COMMANDS
            ) - 1 else ""
            help_message += command.hint()
        console.print(Panel(help_message, title="Commands", border_style="black"))

    @staticmethod
    def is_valid_input(input: str) -> bool:
        """Check if input matches a valid command alias.
        
        Args:
            input (str): User input.
            
        Returns:
            bool
        """
        if input.startswith(CommandPalette.TRIGGER):
            match = re.match(CommandPalette.COMMAND_REGEX, input)     # is command
            return match.group(1) in CommandPalette.ALL_ALIASES if match else False
        else:
            return True     # is regular text

    @staticmethod
    def unrecognized(alias: str) -> None:
        """Handle unrecognized command alias.
        """
        grouped_commands = [
            " ".join(["!" + alias for alias in command.aliases])
            for command in CommandPalette.AVAILABLE_COMMANDS
        ]
        columns = [Panel(group) for group in grouped_commands]
        console.print(Columns(columns))

        error = f"{CommandPalette.TRIGGER + alias}[reset] "
        error += "is not a command.\n"
        error += "Enter [command]!help"
        error += "[reset] or [command]!h[reset] "
        error += "to see available commands."

        console.error(error)

    @staticmethod
    def is_secondary_alias(alias: str) -> bool:
        """Check if alias is not a primary alias 
            (ie: is shortened variant, like `h` for `help`).
           
            Returns:
                bool

        """
        return alias not in CommandPalette.PRIMARY_ALIASES


class CommandCompleter(Completer):
    """Auto-completion for CommandPalette.
    """
    def get_completions(self, document: Any, complete_event: Any) -> Generator:
        from intelliterm.config import config

        # current_position: Point = document.get_menu_position()
        # print(current_position)

        word: str = document.current_line.replace(CommandPalette.TRIGGER, "")
        # word: str = document.get_word_before_cursor(pattern=re.compile(COMMAND_REGEX))
        num_words = len(word.split())

        if num_words == 0:
            # First word (!word)
            for command in CommandPalette.AVAILABLE_COMMANDS:
                for alias in command.aliases:
                    if alias.startswith(word):
                        yield Completion(
                            CommandPalette.TRIGGER + alias,
                            start_position=document.get_start_of_document_position(),
                            style=f"fg:ansi{config.get('accent_color')} bg:black",
                        # selected_style="fg:black bg:red ",
                            display_meta=
                            f"(aliased: {CommandPalette.TRIGGER + command.name})"
                            if CommandPalette.is_secondary_alias(alias) else
                            command.description,
                        )


validator = Validator.from_callable(
    CommandPalette.is_valid_input,
    error_message="Invalid command",
)
