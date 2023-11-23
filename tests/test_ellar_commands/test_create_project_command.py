import os

from ellar.app import App
from ellar.core import Config

from ellar_cli.service import EllarCLIService


def test_create_project_fails_for_py_project_none(cli_runner):
    result = cli_runner.invoke_ellar_command(["create-project", "testing_new_project"])
    assert result.exit_code == 1
    assert result.output == "Error: No pyproject.toml file found.\n"


def test_create_project_fails_for_existing_project_name(
    cli_runner, write_empty_py_project, tmpdir
):
    module_name = "testing_new_project"
    os.makedirs(os.path.join(tmpdir, module_name), exist_ok=True)
    # add_ellar_project_to_py_project("testing_new_project")
    result = cli_runner.invoke_ellar_command(["create-project", module_name])
    assert result.exit_code == 0
    result = cli_runner.invoke_ellar_command(["create-project", module_name])

    assert result.exit_code == 1
    assert result.output == "Error: Ellar Project already exist.\n"


def test_create_project_fails_for_invalid_project_name(
    cli_runner, write_empty_py_project
):
    result = cli_runner.invoke_ellar_command(["create-project", "testing-new-project"])
    assert result.exit_code == 1
    assert result.output == (
        "Error: 'testing-new-project' is not a valid project-name. "
        "Please make sure the project-name is a valid identifier.\n"
    )


def test_create_project_fails_for_existing_module_project_name(
    tmpdir, cli_runner, write_empty_py_project
):
    module_name = "new_project_module"
    with open(os.path.join(tmpdir, module_name + ".py"), mode="w") as fp:
        fp.write("")

    result = cli_runner.invoke_ellar_command(["create-project", module_name])
    assert result.exit_code == 1
    assert result.output == (
        "Error: 'new_project_module' conflicts with the name of an existing "
        "Python module and cannot be used as a project-name. Please try another project-name.\n"
    )


def test_create_project_works_for_existing_folder_with_same_project_name(
    tmpdir, cli_runner, write_empty_py_project
):
    module_name = "new_project_module_2"
    os.makedirs(os.path.join(tmpdir, module_name), exist_ok=True)

    result = cli_runner.invoke_ellar_command(["create-project", module_name])
    assert result.exit_code == 0, result.stderr
    assert result.output == (
        "`new_project_module_2` project scaffold completed. To start your server, run the command below\n"
        "ellar --project new_project_module_2 runserver --reload\n"
        "Happy coding!\n"
    )


def test_create_project_command_works(tmpdir, process_runner, write_empty_py_project):
    result = process_runner(["ellar", "create-project", "ellar_project"])
    assert result.returncode == 0, result.stderr
    assert result.stdout.decode("utf8") == (
        "`ellar_project` project scaffold completed. To start your server, run the command below\n"
        "ellar --project ellar_project runserver --reload\n"
        "Happy coding!\n"
    )
    ellar_cli_service = EllarCLIService.import_project_meta()
    assert ellar_cli_service._meta.dict() == {
        "project_name": "ellar_project",
        "application": "ellar_project.server:application",
        "config": "ellar_project.config:DevelopmentConfig",
        "root_module": "ellar_project.root_module:ApplicationModule",
    }

    application = ellar_cli_service.import_application()
    assert isinstance(application, App)


def test_create_project_command_works_with_specific_directory(
    tmpdir, process_runner, write_empty_py_project
):
    result = process_runner(["ellar", "create-project", "ellar_project", "Another/me"])
    assert result.returncode == 0, result.stderr
    assert result.stdout.decode("utf8") == (
        "`ellar_project` project scaffold completed. To start your server, run the command below\n"
        "ellar --project ellar_project runserver --reload\n"
        "Happy coding!\n"
    )
    ellar_cli_service = EllarCLIService.import_project_meta()
    assert ellar_cli_service._meta.dict() == {
        "project_name": "ellar_project",
        "application": "another.me.ellar_project.server:application",
        "config": "another.me.ellar_project.config:DevelopmentConfig",
        "root_module": "another.me.ellar_project.root_module:ApplicationModule",
    }
    application = ellar_cli_service.import_application()
    assert isinstance(application, App)
    config = ellar_cli_service.get_application_config()
    assert isinstance(config, Config)
    assert ellar_cli_service.import_root_module()
