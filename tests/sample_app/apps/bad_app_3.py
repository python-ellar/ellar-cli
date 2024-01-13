#!/bin/env python
from ellar.app import AppFactory
from ellar.samples import HomeModule

from ellar_cli.main import create_ellar_cli


def bootstrap():
    AppFactory.create_app(modules=[HomeModule])


cli = create_ellar_cli("apps.bad_app_3:bootstrap")

if __name__ == "__main__":
    cli()
