#!/bin/env python
from ellar.app import AppFactory
from ellar.samples import HomeModule

from ellar_cli.main import create_ellar_cli


def bootstrap():
    application = AppFactory.create_app(modules=[HomeModule])
    return application


cli = create_ellar_cli("apps.bad_app_2:bootstrap_unknown")

if __name__ == "__main__":
    cli()
