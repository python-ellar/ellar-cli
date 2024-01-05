import typing as t

import ellar
import uvicorn

import ellar_cli
import ellar_cli.click as click
from ellar_cli.constants import ELLAR_PROJECT_NAME

from .click import EllarCommandGroup
from .manage_commands import create_module, create_project, new_command, runserver

__all__ = ["app_cli"]


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


@click.group(
    name="Ellar CLI Tool... ",
    cls=EllarCommandGroup,
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
def app_cli(ctx: click.Context, project: str) -> None:
    ctx.meta[ELLAR_PROJECT_NAME] = project


app_cli.command(name="new")(new_command)
app_cli.command(
    context_settings={"auto_envvar_prefix": "UVICORN"}, with_app_context=False
)(runserver)
app_cli.command(name="create-project")(create_project)
app_cli.command(name="create-module")(create_module)
