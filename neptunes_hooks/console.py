import logging
from typing import Optional, Union

from rich.console import Console, JustifyMethod
from rich.panel import Panel
from rich.style import Style

LOGGER = logging.getLogger(__name__)


class ConsoleLog:
    def __init__(self, name: str):
        self.console = Console()
        self.logger = logging.getLogger(name)
        self.name = name

    def panel(
        self,
        title: str,
        style: Optional[Union[str, Style]] = None,
        expand: bool = True,
        justify: Optional[JustifyMethod] = None,
    ):
        self.console.print(Panel(title, expand=expand), style=style, justify=justify)
        self.logger.info(title)

    def rule(self, title: str, style: Optional[Union[str, Style]] = None):
        self.console.rule(title=title, style=style)
        self.logger.info(title)

    def print(self, text: str, style: Optional[Union[str, Style]] = None):
        self.console.print(text, style=style)
        self.logger.info(text)
