import os
import random
import subprocess
from configparser import ConfigParser, SectionProxy
from typing import Any

from prompt_toolkit.shortcuts import confirm
from rich.columns import Columns
from rich.panel import Panel

from intelliterm.command_palette import CommandPalette
from intelliterm.console import console
from intelliterm.constants import USER_DATA_DIR
from intelliterm.notifications import notification
from intelliterm.utils import TIPS, logger, longest_line, pretty_dict


class Config:
    """Intelliterm configurations manager.
    
    Methods:
        exists() -> bool:
            Check if configuration file exists.
        default() -> ConfigParser:
            Get default configuration.
        active() -> SectionProxy:
            Get active configuration.
        show() -> None:
            Display active and available configurations.
        get(property: Optional[str] = None) -> str:    
            Get property in active configuration.
        edit() -> None:
            Edit configurations file.
        load() -> None:
            Load configurations file. 
        use(config_name: str) -> None:
            Use a different configuration.
        reset() -> None:
            Reset to default configurations file.
    """

    CONFIG_PATH = os.path.join(USER_DATA_DIR, "config.ini")

    def __init__(self) -> None:
        self.config: ConfigParser = ConfigParser()
        self.load()

    @staticmethod
    def exists() -> bool:
        """Check if configuration file exists.
        """
        return os.path.exists(Config.CONFIG_PATH) and os.path.isfile(Config.CONFIG_PATH)

    @staticmethod
    def default() -> ConfigParser:
        """Get default configuration.
        """        
        default_config = ConfigParser(default_section='GPT3')
        default_config['DEFAULT'] = {
            "model": "gpt-3.5-turbo",
            "temperature": "0",
            "presence_penalty": "0",
            "frequency_penalty": "0",
            "accent_color": "blue"
        }
        default_config['GPT3'] = {
            "model": "gpt-3.5-turbo",
        }
        default_config['GPT4'] = {
            "model": "gpt-4",
        }
        default_config['CONFIG'] = {
            "active": 'GPT3',
        }

        return default_config

    def active(self) -> SectionProxy:
        """Get active configuration.
        """
        return self.config[self.config['CONFIG']['active']]

    def show(self) -> None:
        """Display active and available configurations.
        """
        panels: list[Panel] = []

        for section in self.config:
            if section != "CONFIG" and section != "DEFAULT":
                pretty_config = pretty_dict(
                    dict(self.config[section]),
                    colors=section == self.active().name,
                )

                if section == self.active().name:
                    content = (
                        f"[{self.get('accent_color')}][bold]{section}[reset]" + "\n" +
                        ("-" * longest_line(pretty_config) + "\n") + pretty_config
                    )

                    panels.append(
                        Panel(
                            content,
                            border_style=self.get('accent_color'),
                            title="(active)",
                            title_align="right"
                        )
                    )
                else:
                    panels.append(
                        Panel((
                            section + "\n" + ("-" * longest_line(pretty_config)) + "\n"                            
                        ) + pretty_config,
                            border_style="black")
                    )

        config_command = CommandPalette.get_command('config')

        if config_command:
            if config_command and config_command.args:
                console.print(
                    Panel(
                        Columns(panels),
                        title="[bold]:gear: Configurations",
                        subtitle=(random.choice(TIPS['config'])),
                        title_align="left",
                        subtitle_align="left",
                        border_style="black"
                    )
                )

    def get(self, property: str) -> str:
        """Get property in active configuration.
        
        Args:
            property (str): Property to get from active configuration.
            
        Returns:
            str: Value for property if not None, else, name of active configuration.
        """
        return self.active()[property]

    def edit(self) -> None:
        """Edit configurations file.
        """
        subprocess.run([os.environ.get("EDITOR", "nano"), Config.CONFIG_PATH])
        self.load()
        self.show()

    def validate(self) -> None:
        # TODO(finish)
        required_values: dict[str, Any] = {
            "": {}
        }

        for section, keys in required_values.items():
            if section not in self.config:
                raise Exception(f"Missing section {section} in config")

    def load(self) -> None:
        """Load configurations file.
        """
        if not self.exists():
            os.makedirs(os.path.dirname(Config.CONFIG_PATH), exist_ok=True)
            with open(Config.CONFIG_PATH, "w+") as file:
                self.default().write(file)
                logger.info("Configurations file not found, set to default")
        self.config.read(Config.CONFIG_PATH)

    def use(self, config_name: str) -> None:
        """Use a different configuration.
        
        Args:
            config_name (str): Name of configuration to set as active.
        """
        config_name = config_name.upper()     # case-insensitive

        self.config.read(Config.CONFIG_PATH)

        if config_name != "CONFIG" and self.config.has_section(config_name):
            self.config.set("CONFIG", "active", config_name)

            with open(Config.CONFIG_PATH, "w+") as config_file:
                self.config.write(config_file)
                self.load()
                notification.emit(f"Switched to <strong>{self.active().name}</strong>")
                logger.info(f"{self.active().name} {dict( self.active())}")
        else:
            console.error(f"No configuration named {config_name}")
            logger.info(f"No configuration named {config_name}")
            self.show()

    def reset(self) -> None:
        """Reset to default configurations file.
        """
        yes: bool = confirm("Reset to default configuration?")

        if yes:
            with open(Config.CONFIG_PATH, "w+") as config_file:
                self.default().write(config_file)
                logger.info(f"{Config.CONFIG_PATH} reset to defaults")
            self.load()
            self.show()

    def to_dict(self) -> dict:
        """Transform config to dictionary.

        Returns:
            dict[str, str]
        """
        return {
            section: dict(self.config[section])
            for section in self.config.sections()
        }


config = Config()
