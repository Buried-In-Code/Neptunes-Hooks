import logging
from typing import Any, Optional

from rich import inspect
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.theme import Theme


class ConsoleLog:
    def __init__(self, name: str):
        self.console = Console(
            theme=Theme(
                {
                    "prompt": "cyan",
                    "prompt.choices": "dim green",
                    "prompt.default": "italic green",
                    "logging.level.debug": "dim blue",
                    "logging.level.info": "dim white",
                    "logging.level.warning": "yellow",
                    "logging.level.error": "red",
                    "logging.level.critical": "magenta",
                    "json.key": "bold green",
                    "json.brace": "white",
                    "json.str": "yellow",
                    "json.number": "magenta",
                    "json.null": "italic white",
                }
            )
        )
        self.logger = logging.getLogger(name)

    def panel(self, title: str, style: Optional[str] = None, expand: bool = True):
        self.console.print(Panel(title, expand=expand), style=style, justify="center")
        self.logger.info(title)

    def rule(self, title: str, text_style: str = "rule.line", line_style: str = "rule.line"):
        self.console.rule(title=f"[{text_style}]{title}[/]", style=line_style)
        self.logger.info(title)

    def print_dict(self, data: Any, title: Optional[str] = None, subtitle: Optional[str] = None):
        json_data = JSON.from_data(
            data,
            indent=2,
            highlight=True,
            skip_keys=False,
            ensure_ascii=True,
            check_circular=True,
            allow_nan=True,
            default=None,
            sort_keys=False,
        )
        self.console.print(Panel(json_data, title=title, subtitle=subtitle), style="logging.level.error")

    def debug(self, text: Optional[str] = None, object_: Any = None):
        if object_:
            inspect(object_, title=text, methods=True)
        else:
            self.console.print(f"[logging.level.debug]{text}[/]")
        self.logger.debug(text)

    def info(self, text: Optional[str] = None, object_: Any = None):
        if object_:
            inspect(object_, title=text)
        else:
            self.console.print(f"[logging.level.info]{text}[/]")
        self.logger.info(text)

    def warning(self, text: Optional[str] = None, object_: Any = None):
        if object_:
            inspect(object_, title=text)
        else:
            self.console.print(f"[logging.level.warning]{text}[/]")
        self.logger.warning(text)

    def error(self, text: Optional[str] = None, object_: Any = None):
        if object_:
            inspect(object_, title=text)
        else:
            self.console.print(f"[logging.level.error]{text}[/]")
        self.logger.error(text)

    def critical(self, text: Optional[str] = None, object_: Any = None):
        if object_:
            inspect(object_, title=text)
        else:
            self.console.print(f"[logging.level.critical]{text}[/]")
        self.logger.critical(text)
