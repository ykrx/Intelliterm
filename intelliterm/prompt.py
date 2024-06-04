# ruff: noqa: E501

import json
import platform
import re
from typing import Any, Literal, Optional, TypedDict, cast

import pyperclip
import tiktoken

import intelliterm
from intelliterm.code import Code
from intelliterm.config import config
from intelliterm.console import console
from intelliterm.notifications import notification

bio = {
    "os": platform.system(),
    "config": config.to_dict(),
}

DEFAULT_ENCODING = "gpt-3.5-turbo"
SPECIAL_PROMPTS = {
    "SYSTEM": f"""
        You are {intelliterm.__name__}, 
        a general knowledge and code assistant running via CLI and specializing in short, straight-to-the-point, intuitive answers.
        
        Use this context for questions about config, environment you are running in: {bio}
        
        If I ask anything that involves who you are, clarify that all information is general/approximate/non-identifying.
        
        If input is a concept: use analogies to related concepts.
        Edit every response to ensure the following rules are always satisfied:
            - Style the following terms as bold in markdown:
                - names of individuals
                - names of companies and corporations
                - names of company products                
                - stock tickers
            - Code snippets must support syntax highlighting
            - Do not explain code that is short or simple, simply 
              respond with the code itself
        Input:
        """.strip(),
    "GIT_DIFF": """
        Generate a commit message, max 50 characters, in conventional format:
        """.strip(),
    "CHAT_TITLE": """Summarize this in a maximum of 20 characters""",
}

Role = Literal["system", "assistant", "user"]


class Message(TypedDict, total=False):
    content: Any  # TODO: add multi-modal support
    role: Role


class Prompt:
    """Class representing a chat prompt.

    Attributes:
        role (Role): Role to assume. Defaults to "user".
        content (str): Prompt content.
        is_file (bool): File input flag.

    Methods:
        copy(options: Optional[list[str]] = None) -> None:
            Copy prompt content/code to the clipboard.
        to_message() -> dict[str, str]:
            Transform to OpenAI Chat Completion message.
        token_count() -> int:
            Count number of tokens in prompt content.
        get_code() -> Optional[Code]:
            Extract code from prompt content.
    """

    def __init__(
        self,
        is_file: bool = False,
        content: str = "",
        role: Role = "user",
        took: Optional[float] = None,
    ) -> None:
        self.is_file: bool = is_file
        self.content: str = content
        self.role: Role = role
        self.took: float = 0

    def serialize(self) -> dict[str, Any]:
        return self.__dict__

    @classmethod
    def deserialize(cls, json_str: str) -> "Prompt":
        dict = json.loads(json_str)
        return cast(Prompt, dict)

    def token_count(self) -> int:
        """Count number of tokens in prompt content.

        Returns:
            int: Number of tokens in prompt content.
        """
        encoding = tiktoken.encoding_for_model(
            config.get("model")
            if config.get("model").startswith("gpt")
            else DEFAULT_ENCODING
        )
        num_tokens = len(encoding.encode(self.content))
        return num_tokens

    def copy(self, options: Optional[list[str]] = None) -> None:
        """Copy prompt content or code to clipboard.

        Args:
            options (Optional[list[str]]):
                Copy command options. Defaults to None.
        """

        def _copy_to_clipboard(text: str) -> None:
            if len(text) == 0:
                console.print("Nothing to copy")
                return
            pyperclip.copy(text)

        if options is not None and len(options) > 0:
            match options[0]:
                case "code":
                    # > `!c code`
                    # Copy code in content.
                    code_blocks = self.parse_code()

                    if len(code_blocks) == 1:
                        _copy_to_clipboard(code_blocks[0].code)
                        console.with_divider(":clipboard: code copied!")
                    elif len(code_blocks) > 1:
                        # TODO(implement): handle multiple code blocks
                        pass
                    else:
                        notification.emit("No code to copy")
        else:
            # > !c
            # Copy all content.
            if len(self.content) > 0:
                _copy_to_clipboard(self.content)
                console.with_divider(":clipboard: copied!")

    def get_message(self) -> Message:
        return {"role": self.role, "content": self.content}

    def parse_code(self) -> list[Code]:
        """Extract code blocks from prompt content.

        Returns:
            list[Code]
        """
        found_code_blocks = re.findall(r"```(\w+)\n([\s\S]*?)\n```", self.content)
        code_blocks: list[Code] = []

        for found in found_code_blocks:
            language = found[0]
            code = found[1]
            code_blocks.append(Code(language, code))
        return code_blocks
