import os
from enum import Enum

import anthropic
import openai
from rich.live import Live
from rich.markdown import Markdown

from intelliterm.config import config
from intelliterm.console import console
from intelliterm.constants import CODE_THEME
from intelliterm.prompt import Message, Prompt


class Backend(Enum):
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"


class Client:
    def __init__(self, backend: Backend):
        self.backend = backend
        self.anthropic_client: anthropic.Anthropic

        if backend == Backend.OPENAI:
            openai.api_key = os.getenv("OPENAI_API_KEY")
        elif backend == Backend.ANTHROPIC:
            self.anthropic_client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        else:
            raise ValueError("Invalid backend specified")

    def get_openai_response(
        self,
        prompt: Prompt,
        context: list[Prompt],
        markdown: Markdown,
    ) -> str | None:
        try:
            stream = openai.ChatCompletion.create(
                model=config.get("model"),
                messages=[prompt.get_message() for prompt in context],
                temperature=float(config.get("temperature")),
                presence_penalty=float(config.get("presence_penalty")),
                frequency_penalty=float(config.get("frequency_penalty")),
                stream=True,
            )

            full_content = ""

            with Live(
                markdown,
                console=console,
                transient=False,
                refresh_per_second=40,
                vertical_overflow="visible",
            ) as live:
                messages = []
                for chunk in stream:
                    message = chunk["choices"][0]["delta"]
                    messages.append(message)
                    full_content = "".join([m.get("content", "") for m in messages])
                    markdown = Markdown(full_content, code_theme=CODE_THEME)
                    live.update(markdown)
            stream.close()
            return full_content
        except openai.InvalidRequestError as e:
            console.print("openai:", e)
            return None

    def get_anthropic_response(
        self,
        prompt: Prompt,
        context: list[Prompt],
        markdown: Markdown,
    ) -> str | None:
        try:
            system_message = " ".join(
                [
                    prompt.get_message()["content"]
                    for prompt in context
                    if prompt.get_message()["role"] == "system"
                ]
            )
            messages = [
                prompt.get_message()
                for prompt in context
                if prompt.get_message()["role"] != "system"
            ]
            stream = self.anthropic_client.messages.create(  # type: ignore
                max_tokens=1024,
                system=system_message,
                messages=messages,  # type: ignore
                model=config.get("model"),
                stream=True,
            )

            full_content = ""

            with Live(
                markdown,
                console=console,
                transient=False,
                refresh_per_second=40,
                vertical_overflow="visible",
            ) as live:
                messages = []
                for event in stream:
                    if event.type == "content_block_delta":  # type: ignore
                        message = event.delta.text  # type: ignore
                        messages.append(Message(content=message, role="user"))
                        full_content = "".join([m.get("content", "") for m in messages])
                        markdown = Markdown(full_content, code_theme=CODE_THEME)
                        live.update(markdown)
            stream.close()  # type: ignore
            return full_content
        except anthropic.APIConnectionError as e:
            console.print("The server could not be reached")
            console.print(e.__cause__)
        except anthropic.RateLimitError:
            console.print("A 429 status code was received; we should back off a bit.")
        except anthropic.APIStatusError as e:
            console.print("Another non-200-range status code was received")
            console.print(e.status_code)
            console.print(e.response)
            console.print(e.message)
        return None

    def get_response(
        self,
        prompt: Prompt,
        context: list[Prompt],
        markdown: Markdown,
    ) -> str | None:
        if self.backend == Backend.OPENAI:
            return self.get_openai_response(prompt, context, markdown)
        elif self.backend == Backend.ANTHROPIC:
            return self.get_anthropic_response(prompt, context, markdown)
        else:
            raise ValueError("Invalid backend specified")
