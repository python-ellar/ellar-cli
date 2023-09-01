import getopt
import sys
import typing as t

import click
import typer
from ellar.common.commands import EllarTyper
from ellar.common.constants import CALLABLE_COMMAND_INFO, MODULE_METADATA
from ellar.core.factory import AppFactory
from ellar.core.modules import ModuleSetup
from ellar.core.services import Reflector
from typer.models import CommandInfo

from ellar_cli.constants import ELLAR_META

from .manage_commands import create_module, create_project, new_command, runserver
from .service import EllarCLIService
from .typer import EllarCLITyper

__all__ = ["build_typers", "_typer", "typer_callback"]


_typer = EllarCLITyper(name="ellar")
_typer.command(name="new")(new_command)
_typer.command()(runserver)
_typer.command(name="create-project")(create_project)
_typer.command(name="create-module")(create_module)


@_typer.callback()
def typer_callback(
    ctx: typer.Context,
    project: t.Optional[str] = typer.Option(
        None,
        "-p",
        "--project",
        show_default=True,
        exists=True,
        help="Run Specific Command on a specific project",
    ),
) -> None:
    meta_: t.Optional[EllarCLIService] = EllarCLIService.import_project_meta(project)
    ctx.meta[ELLAR_META] = meta_


def build_typers() -> t.Any:  # pragma: no cover
    app_name: t.Optional[str] = None
    try:
        argv = list(sys.argv)
        options, args = getopt.getopt(
            argv[1:],
            "hp:",
            ["project=", "help"],
        )
        for k, v in options:
            if k in ["-p", "--project"] and v:
                app_name = v
    except Exception as ex:
        click.echo(ex)

    meta_: t.Optional[EllarCLIService] = EllarCLIService.import_project_meta(app_name)

    if meta_ and meta_.has_meta:
        module_configs = AppFactory.get_all_modules(
            ModuleSetup(meta_.import_root_module())
        )
        reflector = Reflector()

        for module_config in module_configs:
            typers_commands = (
                reflector.get(MODULE_METADATA.COMMANDS, module_config.module) or []
            )
            for typer_command in typers_commands:
                if isinstance(typer_command, EllarTyper):
                    _typer.add_typer(typer_command)
                elif hasattr(typer_command, CALLABLE_COMMAND_INFO):
                    command_info: CommandInfo = typer_command.__dict__[
                        CALLABLE_COMMAND_INFO
                    ]
                    _typer.registered_commands.append(command_info)
                elif isinstance(typer_command, click.Command):
                    _typer.add_click_command(typer_command)
