#!/bin/env python
import click
from ellar.app import AppFactory
from ellar.samples import HomeModule

from ellar_cli.main import create_ellar_cli


def bootstrap():
    application = AppFactory.create_app(modules=[HomeModule])
    return application


cli = create_ellar_cli("apps.good_app:bootstrap")


@cli.command()
def working():
    click.echo("Working")


if __name__ == "__main__":
    cli()
