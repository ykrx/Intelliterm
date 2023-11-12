from time import sleep
from intelliterm.console import console


class Notification:
    def __init__(self) -> None:
        self._message: str = ""
        self._read: bool = True

    @property
    def message(self) -> str:
        self._read = True
        return self._message

    @message.setter
    def message(self, message: str) -> None:
        self._message = message

    @property
    def read(self) -> bool:
        return self._read

    def emit(self, message: str) -> None:
        self.message = message
        sleep(0.01)     # TODO(refactor): currently a workaround for bottom_toolbar
        self._read = False
        console.info(message)


notification = Notification()
