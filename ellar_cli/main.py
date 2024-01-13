import typing as t

import ellar
import uvicorn

import ellar_cli
import ellar_cli.click as click
from ellar_cli.constants import ELLAR_PROJECT_NAME

from .click import EllarCommandGroup
from .manage_commands import create_module, create_project, new_command, runserver

__all__ = ["app_cli", "create_ellar_cli"]


def version_callback(ctx: click.Context, _: t.Any, value: bool) -> None:
    if value:
        click.echo("<===========================================================>")
        click.echo(f"        Ellar CLI Version: {ellar_cli.__version__}        ")
        click.echo("    ---------------------------------------------------    ")
        click.echo(f"        Ellar Version: {ellar.__version__}                ")
        click.echo("    ---------------------------------------------------    ")
        click.echo(f"        Uvicorn Version: {uvicorn.__version__}            ")
        click.echo("<============================================================>")
        raise click.Exit(0)


def create_ellar_cli(app_import_string: t.Optional[str] = None) -> click.Group:
    @click.group(
        name="Ellar CLI Tool... ",
        cls=EllarCommandGroup,
        app_import_string=app_import_string,
        help="Ellar, ASGI Python Web framework",
    )
    @click.option(
        "--project",
        show_default=True,
        default="default",
        help="Run Specific Command on a specific project",
    )
    @click.option(
        "-v",
        "--version",
        callback=version_callback,
        help="Show the version and exit.",
        is_flag=True,
        expose_value=False,
        is_eager=True,
    )
    @click.pass_context
    def _app_cli(ctx: click.Context, **kwargs: t.Any) -> None:
        ctx.meta[ELLAR_PROJECT_NAME] = kwargs["project"]

    if not app_import_string:
        _app_cli.command(name="new")(new_command)
        _app_cli.command(name="create-project")(create_project)

    _app_cli.command(context_settings={"auto_envvar_prefix": "UVICORN"})(runserver)
    _app_cli.command(name="create-module")(create_module)

    return _app_cli  # type:ignore[no-any-return]


app_cli = create_ellar_cli()
