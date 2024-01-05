from ellar_cli.main import app_cli


@app_cli.command()
def without_context_command():
    print("Working outside context")


@app_cli.command()
async def without_context_command_async():
    print("Working outside context Async")


def test_working_outside_app_context(cli_runner):
    res = cli_runner.invoke(without_context_command)
    assert res.exit_code == 0
    assert res.output == "Working outside context\n"


def test_working_outside_app_context_async(cli_runner):
    res = cli_runner.invoke(without_context_command_async)
    assert res.exit_code == 0
    assert res.output == "Working outside context Async\n"
