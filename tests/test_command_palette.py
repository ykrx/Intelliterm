import pytest

from intelliterm.command_palette import (
    AVAILABLE_COMMANDS,
    COMMAND_TRIGGER,
    Command,
    CommandPalette,
)


class TestCommandPalette():
    alias_expected_command_name = [(alias, command.name)
                                   for command in AVAILABLE_COMMANDS
                                   for alias in command.aliases]
    command_name_expected_aliases = [(command.name, command.aliases)
                                     for command in AVAILABLE_COMMANDS
                                     for alias in command.aliases]

    @pytest.mark.parametrize(
        "alias, expected_command_name", alias_expected_command_name
    )
    def test_get_command_by_alias(self, alias: str, expected_command_name: str) -> None:
        command = CommandPalette.get_command(alias)
        if expected_command_name is None:
            assert command is None
        else:
            assert isinstance(command, Command)
            assert command.name == expected_command_name

    @pytest.mark.parametrize(
        "command_name, expected_aliases", command_name_expected_aliases
    )
    def test_get_aliases(self, command_name: str, expected_aliases: list[str]) -> None:
        aliases = CommandPalette.get_aliases(command_name)
        assert aliases == expected_aliases

    def test_is_valid_input(self) -> None:
        should_fail = [COMMAND_TRIGGER + x for x in ["bla", "yulian", "jars"]]
        should_pass = [COMMAND_TRIGGER + command.name for command in AVAILABLE_COMMANDS]

        for x in should_fail:
            assert not CommandPalette.is_valid_input(x)
        for x in should_pass:
            assert CommandPalette.is_valid_input(x)
