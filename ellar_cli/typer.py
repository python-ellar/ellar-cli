import sys
import typing as t
from dataclasses import dataclass

import click
from typer import Typer
from typer.main import _typer_developer_exception_attr_name, except_hook, get_command
from typer.models import DeveloperExceptionConfig


@dataclass
class _TyperClickCommand:
    command: click.Command
    name: t.Optional[str]


class EllarCLITyper(Typer):
    """
    Adapting Typer and Click Commands
    """

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self._click_commands: t.List[_TyperClickCommand] = []

    def add_click_command(
        self, cmd: click.Command, name: t.Optional[str] = None
    ) -> None:
        self._click_commands.append(_TyperClickCommand(command=cmd, name=name))

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        if sys.excepthook != except_hook:
            sys.excepthook = except_hook  # type: ignore[assignment]
        try:
            typer_click_commands = get_command(self)
            for item in self._click_commands:
                typer_click_commands.add_command(item.command, item.name)  # type: ignore[attr-defined]
            return typer_click_commands(*args, **kwargs)
        except Exception as e:
            # Set a custom attribute to tell the hook to show nice exceptions for user
            # code. An alternative/first implementation was a custom exception with
            # raise custom_exc from e
            # but that means the last error shown is the custom exception, not the
            # actual error. This trick improves developer experience by showing the
            # actual error last.
            setattr(
                e,
                _typer_developer_exception_attr_name,
                DeveloperExceptionConfig(
                    pretty_exceptions_enable=self.pretty_exceptions_enable,
                    pretty_exceptions_show_locals=self.pretty_exceptions_show_locals,
                    pretty_exceptions_short=self.pretty_exceptions_short,
                ),
            )
            raise e
