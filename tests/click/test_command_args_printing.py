import ellar_cli.click as click
from ellar_cli.main import app_cli

output_1 = """Usage: args-print <arg1> [<arg2>] [OPTIONS]

ARGUMENTS:
  arg1: <arg1>    Arg1 description  [required]
  arg2: [<arg2>]  Arg2 description

[OPTIONS]:
  --help  Show this message and exit.
"""

output_2 = """Usage: args-print-no-description <arg1> [<arg2>] [OPTIONS]

ARGUMENTS:
  arg1: <arg1>    [required]
  arg2: [<arg2>]

[OPTIONS]:
  --help  Show this message and exit.
"""


@app_cli.command()
@click.argument("arg1", required=True, help="Arg1 description")
@click.argument("arg2", required=False, help="Arg2 description")
def args_print(arg1, arg2):
    print(f"ARG1={arg1} ARG2={arg2}")


@app_cli.command()
@click.argument("arg1", required=True)
@click.argument("arg2", required=False)
def args_print_no_description(arg1, arg2):
    print(f"ARG1={arg1} ARG2={arg2}")


def test_args_printing_case_1(cli_runner):
    res = cli_runner.invoke(
        args_print,
        [
            "--help",
        ],
    )
    assert res.exit_code == 0
    assert res.output == output_1


def test_args_printing_case_2(cli_runner):
    res = cli_runner.invoke(
        args_print_no_description,
        [
            "--help",
        ],
    )
    assert res.exit_code == 0
    assert res.output == output_2
