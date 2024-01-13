import pytest

import ellar_cli.click as click
from ellar_cli.main import app_cli


@app_cli.command()
def without_context_command():
    print("Working outside context")


@app_cli.command()
@click.run_as_async
async def without_context_command_async():
    print("Working outside context Async")


@click.command()
@click.argument("name")
@click.run_as_async
async def print_name(name: str):
    click.echo(f"Hello {name}, this is an async command.")


def test_working_outside_app_context(cli_runner):
    res = cli_runner.invoke(without_context_command)
    assert res.exit_code == 0
    assert res.output == "Working outside context\n"


def test_working_outside_app_context_async(cli_runner):
    res = cli_runner.invoke(without_context_command_async)
    assert res.exit_code == 0
    assert res.output == "Working outside context Async\n"


def test_print_name_works(cli_runner):
    res = cli_runner.invoke(print_name, ["Ellar"])
    assert res.exit_code == 0
    assert res.output == "Hello Ellar, this is an async command.\n"


def test_run_as_async_fails():
    with pytest.raises(AssertionError):

        @click.run_as_async
        def print_name_1(name: str):
            pass
