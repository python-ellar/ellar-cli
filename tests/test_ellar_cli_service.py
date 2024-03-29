import os
import subprocess

import pytest
from ellar.app import App
from ellar.core import ConfigDefaultTypesMixin, ModuleBase

from ellar_cli.service import (
    EllarCLIException,
    EllarCLIService,
    EllarPyProject,
)
from ellar_cli.service.pyproject import PY_PROJECT_TOML

good_app_info = (
    b"Usage: good_app.py [OPTIONS] COMMAND [ARGS]...\n\n  "
    b"Ellar, ASGI Python Web framework\n\nOptions:\n  --project TEXT  "
    b"Run Specific Command on a specific project  [default:\n                  "
    b"default]\n  -v, --version   Show the version and exit.\n  --help          "
    b"Show this message and exit.\n\nCommands:\n  create-module  - Scaffolds Ellar Application Module -\n  "
    b"failing-1\n  failing-2\n  failing-3\n  runserver      - "
    b"Starts Uvicorn Server -\n  working\n"
)


def test_import_project_meta_returns_default_when_py_project_is_none(tmp_path):
    os.chdir(tmp_path)
    meta = EllarCLIService.import_project_meta()
    assert meta is None


def test_import_project_meta_returns_default_when_py_project_does_not_have_ellar_project_data(
    tmpdir, write_empty_py_project
):
    ellar_cli_service = EllarCLIService.import_project_meta()
    assert ellar_cli_service._meta is None
    assert ellar_cli_service.py_project_path == os.path.join(tmpdir, PY_PROJECT_TOML)
    assert ellar_cli_service.cwd == tmpdir
    assert ellar_cli_service.app == "ellar"
    assert ellar_cli_service.ellar_py_projects.default_project is None
    assert ellar_cli_service.ellar_py_projects.has_default_project is False


def test_import_project_meta_returns_default_project_when_project_is_none(
    add_ellar_project_to_py_project,
):
    add_ellar_project_to_py_project("some-project")

    ellar_cli_service = EllarCLIService.import_project_meta()

    assert ellar_cli_service._meta.dict(by_alias=False) == {
        "project_name": "some-project",
        "application": "some-project.server:bootstrap",
        "config": "some-project.config:DevelopmentConfig",
        "root_module": "some-project.root_module:ApplicationModule",
    }
    assert ellar_cli_service.app == "some-project"
    assert ellar_cli_service.ellar_py_projects.default_project == "some-project"
    assert ellar_cli_service.ellar_py_projects.has_default_project


def test_import_project_meta_returns_meta_for_a_project(
    add_ellar_project_to_py_project,
):
    add_ellar_project_to_py_project("some-project")
    add_ellar_project_to_py_project("some-other-project")

    ellar_cli_service = EllarCLIService.import_project_meta("some-other-project")
    assert ellar_cli_service._meta.dict(by_alias=False) == {
        "project_name": "some-other-project",
        "application": "some-other-project.server:bootstrap",
        "config": "some-other-project.config:DevelopmentConfig",
        "root_module": "some-other-project.root_module:ApplicationModule",
    }
    assert ellar_cli_service.app == "some-other-project"
    assert ellar_cli_service.ellar_py_projects.default_project == "some-project"
    assert ellar_cli_service.ellar_py_projects.has_default_project


def test_import_project_meta_returns_default_meta_for_project_name_not_found(
    add_ellar_project_to_py_project,
):
    add_ellar_project_to_py_project("some-project")
    # returns default is it doesn't exist
    ellar_cli_service = EllarCLIService.import_project_meta("does-not-exits")
    assert ellar_cli_service.app == "some-project"


def test_import_project_meta_returns_default_when_both_project_and_ellar_py_project_default_do_not_exist_in_project(
    add_ellar_project_to_py_project,
):
    ellar_cli_service = EllarCLIService.import_project_meta("does-not-exits")
    assert ellar_cli_service
    assert ellar_cli_service._meta is None


def test_cwd_has_pyproject_file_returns_true(write_empty_py_project):
    assert EllarCLIService.cwd_has_pyproject_file()


def test_cwd_has_pyproject_file_returns_false(tmp_path):
    os.chdir(tmp_path)
    assert EllarCLIService.cwd_has_pyproject_file() is False


def test_create_ellar_project_meta_work(
    tmp_path, write_empty_py_project, tmp_py_project_path
):
    cli_service = EllarCLIService(
        py_project_path=tmp_py_project_path,
        ellar_py_projects=write_empty_py_project,
        cwd=str(tmp_path),
    )
    cli_service.create_ellar_project_meta("new-project")
    ellar_cli_service = EllarCLIService.import_project_meta("new-project")
    assert ellar_cli_service._meta.dict(by_alias=False) == {
        "project_name": "new-project",
        "application": "new-project.server:bootstrap",
        "config": "new-project.config:DevelopmentConfig",
        "root_module": "new-project.root_module:ApplicationModule",
    }


def test_create_ellar_project_meta_fails_if_py_project_does_not_exist(
    tmp_path, mock_py_project_table
):
    cli_service = EllarCLIService(
        py_project_path=str(tmp_path / PY_PROJECT_TOML),
        ellar_py_projects=EllarPyProject(mock_py_project_table),
        cwd=str(tmp_path),
    )
    with pytest.raises(EllarCLIException, match="Could not locate `pyproject.toml`"):
        cli_service.create_ellar_project_meta("new-project")


def test_create_ellar_project_meta_fails_if_project_name_exist(
    tmp_path, tmp_py_project_path, add_ellar_project_to_py_project
):
    ellar_py_project = add_ellar_project_to_py_project("some-project")
    cli_service = EllarCLIService(
        py_project_path=tmp_py_project_path,
        ellar_py_projects=ellar_py_project,
        cwd=str(tmp_path),
    )
    with pytest.raises(
        EllarCLIException,
        match="project -> `some-project` already exist in ellar projects",
    ):
        cli_service.create_ellar_project_meta("some-project")


def test_import_application_works(tmp_path, write_empty_py_project, process_runner):
    result = process_runner(["ellar", "create-project", "new_project_one"])
    assert result.returncode == 0
    ellar_cli_service = EllarCLIService.import_project_meta()
    assert ellar_cli_service._meta.dict(by_alias=False) == {
        "project_name": "new_project_one",
        "application": "new_project_one.server:bootstrap",
        "config": "new_project_one.config:DevelopmentConfig",
        "root_module": "new_project_one.root_module:ApplicationModule",
    }

    application = ellar_cli_service.import_application()
    assert isinstance(application, App)


def test_import_configuration_works(tmpdir, write_empty_py_project, process_runner):
    result = process_runner(["ellar", "create-project", "new_project_two"])
    assert result.returncode == 0, result.stderr

    ellar_cli_service = EllarCLIService.import_project_meta()
    config = ellar_cli_service.import_configuration()

    assert issubclass(config, ConfigDefaultTypesMixin)


def test_import_root_module_works(write_empty_py_project, process_runner):
    result = process_runner(["ellar", "create-project", "new_project_three"])
    assert result.returncode == 0, result.stderr

    ellar_cli_service = EllarCLIService.import_project_meta()
    root_module = ellar_cli_service.import_root_module()

    assert issubclass(root_module, ModuleBase)


def test_version_works(write_empty_py_project, process_runner):
    result = process_runner(["ellar", "--version"])
    assert result.returncode == 0

    assert "Ellar CLI Version:" in str(result.stdout) and "Ellar Version:" in str(
        result.stdout
    )


def test_apps_good_app_cli_works(change_os_dir):
    result = subprocess.run(["python", "apps/good_app.py"], stdout=subprocess.PIPE)
    assert result.returncode == 0
    assert result.stdout == good_app_info


def test_apps_good_app_working_command(change_os_dir):
    result = subprocess.run(
        ["python", "apps/good_app.py", "working"], stdout=subprocess.PIPE
    )
    assert result.returncode == 0
    assert result.stdout == b"Working\n"


def test_apps_good_app_failing_commands(change_os_dir):
    result = subprocess.run(
        ["python", "apps/good_app.py", "failing-1"], stderr=subprocess.PIPE
    )
    assert result.returncode == 1
    assert result.stderr == b"Error: Not Available\n"

    result = subprocess.run(
        ["python", "apps/good_app.py", "failing-2"], stderr=subprocess.PIPE
    )
    assert result.returncode == 1
    assert result.stderr == b"Error: Not Available\n"

    result = subprocess.run(
        ["python", "apps/good_app.py", "failing-3"], stderr=subprocess.PIPE
    )
    assert result.returncode == 1
    assert result.stderr == b"Error: Not Available\n"


def test_apps_bad_app_fails(change_os_dir):
    result = subprocess.run(
        ["python", "apps/bad_app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert result.returncode == 1
    assert (
        result.stderr
        == b"Error: Coroutine Application Bootstrapping is not supported.\n"
    )


def test_apps_bad_app_2_fails(change_os_dir):
    result = subprocess.run(
        ["python", "apps/bad_app_2.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert result.returncode == 1
    assert (
        b'Error: Attribute "bootstrap_unknown" not found in python module'
        in result.stderr
    )


def test_apps_bad_app_3_fails(change_os_dir):
    result = subprocess.run(
        ["python", "apps/bad_app_3.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert result.returncode == 1
    assert (
        result.stderr
        == b"Error: Boostrap Function must return Instance of `ellar.app.App` type\n"
    )
