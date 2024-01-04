from ellar.app import current_app

from ellar_cli.click.group import AppContextGroup

app = AppContextGroup(name="app")


@app.group()
def app_group():
    pass


@app_group.command(with_app_context=False)
def invoke_without_app_context():
    assert current_app.config
    print("Application Context wont be initialized.")


def test_app_group_is_of_type_application_context_group():
    assert isinstance(app_group, AppContextGroup)
    assert len(app_group.commands) == 1
    assert "app-group" in app.commands


def test_invoke_without_app_context_fails(cli_runner):
    res = cli_runner.invoke(invoke_without_app_context)
    assert res.exit_code == 1
