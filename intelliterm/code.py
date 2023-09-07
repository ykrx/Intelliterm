import subprocess

from prompt_toolkit.shortcuts import confirm

from intelliterm.console import console
from intelliterm.notifications import notification


class Code:
    def __init__(self, language: str, code: str) -> None:
        self.language: str = language
        self.code: str = code
        self._confirmed: bool = False

    # TODO(implement): Create venv + install deps (if necessary to run code snippet)
    # TODO(implement): handle multiple code blocks
    def run(self) -> None:
        """Execute code.
        """
        # TODO(fix): doesn't work yet
        if not self._confirmed:
            self._confirmed = confirm(f"Run {self.language} code?")

        if self._confirmed:
            if self.language in ["bash", "zsh", "shell"]:
                console.print(f"[black]({self.language})\n")
                subprocess.run(self.code.split())
            elif self.language == "python":
                console.print("[black](python)\n")
                subprocess.run(["python3", "-c", self.code])
            elif self.language in ["javascript", "typescript"]:
                console.print("[black](node)\n")
                subprocess.run(["node", "-e", self.code])
            else:
                notification.emit(f"Running {self.language} code is not supported yet")
