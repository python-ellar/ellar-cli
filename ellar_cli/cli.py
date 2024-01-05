import os
import sys

import ellar_cli.click as click

from .main import app_cli

__all__ = ["main"]


@app_cli.command()
@click.argument("name")
def say_hi(name: str):
    click.echo(f"Welcome {name}, to Ellar CLI, ASGI Python Web framework\n")


def main():
    sys.path.append(os.getcwd())
    app_cli()


if __name__ == "__main__":  # pragma: no cover
    main()
