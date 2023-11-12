import json
import os
import re
import subprocess
import time
import uuid
from datetime import datetime
from string import punctuation
from typing import Any, Optional, Union

import openai
from emoji import emojize
from pick import pick
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

import intelliterm
from intelliterm.command_palette import CommandPalette, prompt
from intelliterm.config import config
from intelliterm.console import console
from intelliterm.constants import CODE_THEME, SAVED_CHATS_DIR
from intelliterm.notifications import notification
from intelliterm.prompt import SPECIAL_PROMPTS, Prompt
from intelliterm.types import AutoCopy
from intelliterm.utils import get_file_info, logger, pretty_dict

if "OPENAI_API_KEY" not in os.environ:
    console.error("Missing OPENAI_API_KEY")
    console.print("Add \texport OPENAI_API_KEY = 'API-KEY'\t to your .zshrc or .bashrc")
    quit()

openai.api_key = os.getenv("OPENAI_API_KEY")

class Chat:
    """Class representing a chat client.

    Attributes:
        config (Config): Configuration manager.
        _oneshot (bool): If True, exits intelliterm after completion.
        autocopy (bool): Flag for auto-copying last response to clipboard.
            Defaults to "off".
        history (list[str]): List of CommandPalette inputs.
        is_completing (bool): Flag indicating whether chat is completing prompt.
        chat_id (str): Unique identifier for the chat session.
        _context (list[ChatPrompt]): Current chat context.

    Methods:
        configure(options: list[str]) -> None:
            Manage intelliterm configuration.
        oneshot(toggle: bool) -> None:
            Toggle oneshot client.
        history(input: str) -> None:
            Add user input to history.
        context(prompt: Union[Prompt, list[Prompt]]) -> None:
            Add a single prompt or list of prompts to context.
        last_prompt() -> Optional[ChatPrompt]:
            Return last prompt in context.
        new() -> None:
            Start a new chat (clear context).
        total_tokens() -> int:
            Return total number of tokens in current chat's context.
        info() -> str:
            Return current chat's info as formatted string.
        file(path: str, prompt: ChatPrompt) -> None:
            Handle file input.
        create_title() -> str:
            Create a title for the current chat's context.
        save() -> None:
            Save current chat.
        load() -> None:
            Load saved chat.
        ask(prompt: ChatPrompt, show_input: bool = True) -> None:
            Call model completion on a prompt.
        listen() -> None:
            Listen for new prompts/commands.
    """
    def __init__(
        self,
        oneshot: bool = False,
        autocopy: AutoCopy = "off",
    ):
        self._oneshot: bool = oneshot
        self.autocopy: AutoCopy = autocopy
        self._history: list[str] = []
        self.is_completing: bool = False
        self.chat_id: str = str(uuid.uuid4())
        self._context: list[Prompt] = [
            Prompt(content=SPECIAL_PROMPTS['SYSTEM'], role="system")
        ]

    def history(self, input: str) -> None:
        """Add user input to history.

        Args:
            input (str)
        """
        self._history.append(input)

    def context(self, prompt: Union[Prompt, list[Prompt]]) -> None:
        """Add a single prompt or list of prompts to context.

        Args:
            prompt (Union[Prompt, list[Prompt]])
        """
        if isinstance(prompt, list):
            self._context.extend(prompt)
        else:
            self._context.append(prompt)

    def serialize(self) -> dict[str, Any]:
        context = [prompt.serialize() for prompt in self._context]
        obj = {
            "chat_id": self.chat_id,
            "timestamp": str(datetime.now()),
            "_context": context
        }
        return obj

    @classmethod
    def deserialize(cls, json_str: str) -> 'Chat':
        # TODO: sdosdo 
        dict = json.loads(json_str)

        dict.pop('timestamp', None)
        chat = Chat()
        chat.__dict__.update(dict)

        new_context: list[Prompt] = []

        for p in dict['_context']:
            prompt = Prompt()
            prompt.__dict__.update(p)
            new_context.append(prompt)

        chat._context = new_context
        return chat

    def configure(self, options: list[str]) -> None:
        """Handle `!config` command.

        Args:
            options (list[str]): Configuration options.
        """
        if len(options) > 0:
            match options[0]:
                case "reset":
                    config.reset()
                case "edit":
                    # > !config edit
                    config.edit()
                case _:
                    # > !use <config_name>
                    config_name = options[0]
                    config.use(config_name)
        else:
            # > !cfg
            config.show()

    def oneshot(self, toggle: bool) -> None:
        """Toggle oneshot client.

        Args:
            toggle (bool)
        """
        self._oneshot = toggle

    def last_prompt(self) -> Optional[Prompt]:
        """Return last prompt in context.

        Returns:
            Optional[ChatPrompt]: Last prompt in chat. Defaults to None.
        """
        return self._context[-1] if len(self._context) > 1 else None

    def new(self) -> None:
        """Start a new chat (clear context).
        """
        self._context = self._context[:1]     # keep system prompt
        self.chat_id = str(uuid.uuid4())
        console.info("[black]Started new chat")

    def total_tokens(self) -> int:
        """Return total number of tokens in current chat's context.

        Returns:
            int: Total number of tokens in chat's context.
        """
        return sum(prompt.token_count() for prompt in self._context)

    def info(self) -> str:
        """Return current chat's info as formatted string.

        Returns:
            str: Chat info.
        """
        info = ""
        last_prompt = self.last_prompt()
        total_tokens = self.total_tokens()

        if last_prompt:
            info += f"[bold][{config.get('accent_color')}]:gear: {config.active().name} "
            info += f"[reset]([bold]{last_prompt.token_count()} "
            info += f"[reset]token{'s' if last_prompt.token_count() > 1 else ''}, "
            info += f"[bold]{total_tokens} [reset]total)"
        return info

    def file(self, path: str, prompt: Prompt) -> None:
        """Handle file input.
        
        Args:
            path (str): Path to file.
            prompt (ChatPrompt): (ie: what to do with file)
        """
        path = path.replace("~", os.environ['HOME'])

        if os.environ['HOME'] not in path:
            # use cwd
            path = os.path.join(os.getcwd(), path)

        if os.path.exists(path):
            if os.path.isfile(path):
                with open(path, "r") as file:
                    file_info = get_file_info(path)
                    console.print(
                        Panel(
                            pretty_dict(file_info),
                            title="[bold]:open_file_folder: file",
                            border_style="black"
                        )
                    )
                    prompt.content += file.read()
                    self.ask(prompt, show_input=False)
            else:
                # is a dir / not a file
                return
        else:
            console.error(f"{path} does not exist")

    def create_title(self) -> str:
        """Create a title for the current chat's context.

        Returns:
            str: Generated title.
        """
        response = openai.ChatCompletion.create(
            model=config.get("model"),
            messages=([prompt.to_message() for prompt in self._context[1:]] +
                      [Prompt(content=SPECIAL_PROMPTS['CHAT_TITLE']).to_message()]),
            temperature=float(config.get("temperature")),
            presence_penalty=float(config.get("presence_penalty")),
            frequency_penalty=float(config.get("frequency_penalty"))
        )
        title: str = str(response.choices[0].message.content).strip(punctuation)
        title = re.sub(r'[\\/*?:"<>|]', "", title)

        # Duplicate check
        existing_titles = set()
        for filename in os.listdir(SAVED_CHATS_DIR):
            if filename.endswith(".json"):
                existing_titles.add(filename[:-5])

        if title in existing_titles:
            highest_num = 0
            for existing_title in existing_titles:
                match = re.search(rf"{title}_(\d+)$", existing_title)
                if match:
                    number = int(match.group(1))
                    highest_num = max(highest_num, number)

            title = f"{title}_{highest_num + 1}"

        return title

    def save(self) -> None:
        """Save current chat.
        """
        def check_if_saved() -> tuple[bool, Optional[str]]:
            for file_name in os.listdir(SAVED_CHATS_DIR):
                if file_name.endswith(".json"):
                    file_path = os.path.join(SAVED_CHATS_DIR, file_name)
                    with open(file_path) as file:
                        chat = json.loads(file.read())
                        if chat['chat_id'] == self.chat_id:
                            return (True, file_name)
            return (False, None)

        chat_empty = len(self._context) == 1

        if chat_empty:
            notification.emit("Nothing to save (chat empty)")
            return

        saved, saved_name = check_if_saved()

        if saved and saved_name:
            # exists, update existing chat
            file_path = os.path.join(SAVED_CHATS_DIR, saved_name)
        else:
            # does not exist, create new chat
            title = self.create_title()
            file_name = f"{title}.json"
            file_path = os.path.join(SAVED_CHATS_DIR, file_name)

        with open(file_path, "w+") as file:
            chat_dict = self.serialize()
            json.dump(chat_dict, file, indent=4)

            file_path = file_path.replace(os.environ['HOME'], '~')
            logger.info(f"Saved chat ${self.chat_id}: ${file_path}")
            notification.emit(f"[black]Saved chat to: ${file_path}")

    # TODO(add test)
    def load(self) -> None:
        """Load a saved chat.
        """
        file_names: list[str] = []
        chats: list[str] = []

        if os.path.exists(SAVED_CHATS_DIR):
            for file_name in os.listdir(SAVED_CHATS_DIR):
                file_path = os.path.join(SAVED_CHATS_DIR, file_name)

                if os.path.isfile(file_path) and file_name.endswith(".json"):
                    with open(file_path, "r") as file:
                        file_names.append(file_name.split(".")[0])
                        chats.append(file.read())
            if file_names:
                file_name, i = pick(
                    file_names,
                    title="Load chat: ",
                    indicator=">",
                )
                if i is not None:
                    selected_chat = Chat.deserialize(chats[i])
                    self.__dict__.update(selected_chat.__dict__)
                    # self.chat_id = selected_chat.chat_id
                    # self._context = selected_chat._context
                    notification.emit(f'Loaded "{file_name}"')
            else:
                notification.emit("No saved chats")
        else:
            notification.emit("No saved chats")

    def ask(self, prompt: Prompt, show_input: bool = True) -> None:
        """Call model completion on a prompt.

        Args:
            prompt (ChatPrompt)
            show_input (bool): Show/hide input before completion. Defaults to True.
        """
        prompt_message = prompt.to_message()

        console.clear()
        logger.info(prompt_message)

        self.context(prompt)

        if not self._oneshot and show_input:
            console.print(
                Panel(
                    Markdown(prompt.content, code_theme=CODE_THEME),
                    title=self.info(),
                    title_align="right",
                    border_style="black"
                )
            )

        markdown = Markdown("", code_theme=CODE_THEME)
        full_content = ""

        try:
            self.is_completing = True
            start_time = time.time()
            response = openai.ChatCompletion.create(
                model=config.get("model"),
                messages=[prompt.to_message() for prompt in self._context],
                temperature=float(config.get("temperature")),
                presence_penalty=float(config.get("presence_penalty")),
                frequency_penalty=float(config.get("frequency_penalty")),
                stream=True,
            )

            messages = []

            with Live(
                markdown,
                console=console,
                transient=True,
                refresh_per_second=40,
                vertical_overflow="visible"
            ) as live:
                for chunk in response:
                    message = chunk['choices'][0]['delta']
                    messages.append(message)

                    full_content = "".join([m.get("content", "") for m in messages])
                    markdown = Markdown(
                        full_content,
                        code_theme=CODE_THEME,
                    )
                    live.update(markdown)
            response.close()
        except openai.InvalidRequestError as e:
            console.print("openai:", e)
            return None
        except Exception as e:
            console.print(e)
        except (KeyboardInterrupt, EOFError):
            if self.is_completing:
                console.with_divider(":stop_button: aborted")
                return None
        finally:
            self.is_completing = False
            self.context(
                Prompt(
                    content=full_content,
                    role="assistant",
                    took=time.time() - start_time
                )
            )
            console.print(markdown)

        last_prompt = self.last_prompt()

        if last_prompt:
            match self.autocopy:
                case "all":
                    last_prompt.copy()
                case "code":
                    last_prompt.copy(["code"])
                case "off":
                    pass
        else:
            console.with_divider()

        if not self._oneshot:
            self.listen()

    def listen(self) -> None:
        """Listen for new prompts/commands.
        """
        while True:
            try:
                input = prompt()

                if input is not None and len(input) > 0:
                    self.history(input)

                    if input.startswith(CommandPalette.TRIGGER):
                        parts = input[1:].split()
                        alias, options = parts[0], parts[1:]

                        command = CommandPalette.get_command(alias)
                        last_prompt = self.last_prompt()

                        if command:
                            match command.name:
                                case "version":
                                    console.print(f"[reset]{intelliterm.__version__}")
                                case "help":
                                    CommandPalette.help()
                                case "config":
                                    self.configure(options)
                                case "info":
                                    console.print(self.info())
                                case "save":
                                    self.save()
                                case "load":
                                    self.load()
                                case "copy":
                                    if last_prompt:
                                        last_prompt.copy(options)
                                    else:
                                        notification.emit("Nothing to copy")
                                case "run":
                                    if last_prompt:
                                        if last_prompt.parse_code() == []:
                                            notification.emit("No code to run")
                                        else:
                                            last_prompt.parse_code()[0].run()
                                    else:
                                        notification.emit("No code to run")
                                case "file":
                                    if len(options) > 0:
                                        self.file(
                                            options[0],
                                            Prompt(content="".join(options[1:]))
                                        )
                                    else:
                                        console.error("No file specified")
                                        console.print(command.hint())
                                case "new":
                                    self.new()
                                case "shell":
                                    if options and len(options) > 0:
                                        try:
                                            subprocess.run(options, shell=True)
                                        except subprocess.SubprocessError as e:
                                            console.print(e)
                                    else:
                                        console.error("No shell command specified")
                                        console.print(command.hint())
                                case "quit":
                                    quit()
                        else:
                            CommandPalette.unrecognized(alias)
                    else:
                        self.ask(Prompt(content=input))
            except (KeyboardInterrupt, EOFError):
                if self.is_completing:
                    pass
                else:
                    # otherwise: quit intelliterm
                    quit()
