#!/bin/env python
import click
from ellar.app import AppFactory
from ellar.core import Config
from ellar.samples import HomeModule

from ellar_cli.constants import ELLAR_META
from ellar_cli.main import create_ellar_cli
from ellar_cli.service import EllarCLIService


def bootstrap():
    application = AppFactory.create_app(modules=[HomeModule])
    return application


cli = create_ellar_cli("apps.good_app:bootstrap")


@cli.command()
@click.pass_context
def working(ctx: click.Context):
    ellar_cli_service: EllarCLIService = ctx.meta.get(ELLAR_META)
    assert isinstance(ellar_cli_service.get_application_config(), Config)
    click.echo("Working")


@cli.command()
@click.pass_context
def failing_1(ctx: click.Context):
    ellar_cli_service: EllarCLIService = ctx.meta.get(ELLAR_META)
    ellar_cli_service.import_configuration()


@cli.command()
@click.pass_context
def failing_2(ctx: click.Context):
    ellar_cli_service: EllarCLIService = ctx.meta.get(ELLAR_META)
    ellar_cli_service.import_configuration()


@cli.command()
@click.pass_context
def failing_3(ctx: click.Context):
    ellar_cli_service: EllarCLIService = ctx.meta.get(ELLAR_META)
    ellar_cli_service.import_root_module()


if __name__ == "__main__":
    cli()
