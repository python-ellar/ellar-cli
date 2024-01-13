#!/bin/env python
import click
from ellar.app import AppFactory

from ellar_cli.main import create_ellar_cli


async def bootstrap():
    application = AppFactory.create_app()
    return application


cli = create_ellar_cli("apps.bad_app:bootstrap")


@cli.command()
def working():
    click.echo("Working")


if __name__ == "__main__":
    cli()
