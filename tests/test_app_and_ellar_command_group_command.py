import importlib
import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

sample_app_path = os.path.join(Path(__file__).parent, "sample_app")
runserver = importlib.import_module("ellar_cli.manage_commands.runserver")


@pytest.fixture()
def change_os_dir():
    sys.path.append(sample_app_path)
    os.chdir(sample_app_path)
    print(f"working director - {os.getcwd()}")
    yield
    sys.path.remove(sample_app_path)


def test_ellar_command_group_works_for_default_project(change_os_dir):
    result = subprocess.run(["ellar", "db", "create-migration"], stdout=subprocess.PIPE)
    assert result.returncode == 0
    assert result.stdout == b"create migration command\n"


def test_ellar_command_group_works_for_default_project_case_2(change_os_dir):
    result = subprocess.run(["ellar", "whatever-you-want"], stdout=subprocess.PIPE)
    assert result.returncode == 0
    assert result.stdout == b"Whatever you want command\n"


def test_ellar_group_for_specific_project_works(change_os_dir):
    result = subprocess.run(
        ["ellar", "--project", "example_project_2", "db", "create-migration"],
        stdout=subprocess.PIPE,
    )
    assert result.returncode == 0
    assert result.stdout == b"create migration command from example_project_2\n"

    result = subprocess.run(
        ["ellar", "--project", "example_project_2", "db", "create-migration"],
        stdout=subprocess.PIPE,
    )
    assert result.returncode == 0
    assert result.stdout == b"create migration command from example_project_2\n"

    result = subprocess.run(
        ["ellar", "--project", "example_project_2", "say-hi", "Ellar"],
        stdout=subprocess.PIPE,
    )
    assert result.returncode == 0
    assert (
        result.stdout == b"Welcome Ellar, to Ellar CLI, ASGI Python Web framework\n\n"
    )


def test_ellar_group_for_specific_project_works_case_2(change_os_dir):
    result = subprocess.run(
        ["ellar", "--project", "example_project", "whatever-you-want"],
        stdout=subprocess.PIPE,
    )
    assert result.returncode == 0
    assert result.stdout == b"Whatever you want command\n"

    result = subprocess.run(
        ["ellar", "--project", "example_project_2", "whatever-you-want"],
        stdout=subprocess.PIPE,
    )
    assert result.returncode == 0
    assert result.stdout == b"Whatever you want command from example_project_2\n"


def test_help_command(change_os_dir):
    result = subprocess.run(["ellar", "--help"], stdout=subprocess.PIPE)
    assert result.returncode == 0

    result = subprocess.run(
        ["ellar", "--project", "example_project", "--help"], stdout=subprocess.PIPE
    )
    assert result.returncode == 0

    result = subprocess.run(
        ["ellar", "--project", "example_project_2", "--help"], stdout=subprocess.PIPE
    )
    assert result.returncode == 0


def test_click_command_works(change_os_dir):
    result = subprocess.run(["ellar", "say-hello"], stdout=subprocess.PIPE)
    assert result.returncode == 0

    assert result.stdout == b"Hello from ellar.\n"


def test_command_with_context(change_os_dir):
    result = subprocess.run(
        ["ellar", "db", "command-with-context"], stdout=subprocess.PIPE
    )
    assert result.returncode == 0
    assert (
        result.stdout
        == b"Running a command with application context - example_project\n"
    )


def test_command_with_context_async(change_os_dir):
    result = subprocess.run(
        ["ellar", "db", "command-with-context-async"], stdout=subprocess.PIPE
    )
    assert result.returncode == 0
    assert (
        result.stdout
        == b"Running a command with application context in Async Mode - example_project\n"
    )


def test_running_example_project_1_works(cli_runner, change_os_dir):
    with mock.patch.object(runserver, "uvicorn_run") as mock_run:
        result = cli_runner.invoke_ellar_command(
            ["--project", "example_project_1", "runserver"]
        )
        assert result.exit_code == 0

        assert mock_run.called
        assert mock_run.call_args.kwargs["factory"] is False
        assert mock_run.call_args.args == ("example_project.server:application",)


def test_running_example_project_2_works(cli_runner, change_os_dir):
    with mock.patch.object(runserver, "uvicorn_run") as mock_run:
        result = cli_runner.invoke_ellar_command(
            ["--project", "example_project_2", "runserver"]
        )
        assert result.exit_code == 0

        assert mock_run.called
        assert mock_run.call_args.kwargs["factory"] is True
        assert mock_run.call_args.args == ("example_project_2.server:bootstrap",)


def test_running_example_project_3_fails(cli_runner, change_os_dir):
    with mock.patch.object(runserver, "uvicorn_run") as mock_run:
        result = cli_runner.invoke_ellar_command(
            ["--project", "example_project_3", "runserver"]
        )
        assert result.exit_code == 1
        assert (
            result.output
            == "Error: Coroutine Application Bootstrapping is not supported.\n"
        )
        assert mock_run.called is False


def test_running_example_project_3_db_command_fails(cli_runner, change_os_dir):
    result = cli_runner.invoke_ellar_command(
        ["--project", "example_project_3", "db", "create-migration"]
    )
    assert result.exit_code == 1
    assert (
        result.output
        == "Error: Coroutine Application Bootstrapping is not supported.\n"
    )
