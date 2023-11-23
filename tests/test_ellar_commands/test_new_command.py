import os

from ellar_cli.manage_commands.new import NewTemplateScaffold
from ellar_cli.schema import EllarScaffoldSchema
from ellar_cli.service import EllarCLIService


def test_new_command_works(tmpdir, process_runner):
    result = process_runner(["ellar", "new", "ellar-project-new"])
    assert result.returncode == 0, result.stderr
    assert result.stdout.decode("utf8") == (
        "`ellar_project_new` project created successfully.\n"
        "- cd ellar-project-new\n"
        "To start your server, run the command below\n"
        "- ellar --project ellar_project_new runserver --reload\n"
        "Happy coding!\n"
    )
    os.chdir(os.path.join(tmpdir, "ellar-project-new"))
    ellar_cli_service = EllarCLIService.import_project_meta()
    assert ellar_cli_service._meta.dict() == {
        "project_name": "ellar_project_new",
        "application": "ellar_project_new.server:application",
        "config": "ellar_project_new.config:DevelopmentConfig",
        "root_module": "ellar_project_new.root_module:ApplicationModule",
    }


def test_new_command_works_with_specific_directory_case_1(tmpdir, process_runner):
    result = process_runner(["ellar", "new", "ellar-project-new", "Another/me"])
    assert result.returncode == 0, result.stderr
    assert result.stdout.decode("utf8") == (
        "`ellar_project_new` project created successfully.\n"
        "- cd another/me\n"
        "To start your server, run the command below\n"
        "- ellar --project ellar_project_new runserver --reload\n"
        "Happy coding!\n"
    )
    os.chdir(os.path.join(tmpdir / "another/me"))
    ellar_cli_service = EllarCLIService.import_project_meta()
    assert ellar_cli_service._meta.dict() == {
        "project_name": "ellar_project_new",
        "application": "ellar_project_new.server:application",
        "config": "ellar_project_new.config:DevelopmentConfig",
        "root_module": "ellar_project_new.root_module:ApplicationModule",
    }


def test_new_command_works_with_specific_directory_case_3(tmpdir, process_runner):
    _path = tmpdir / "23-August-2023"
    os.makedirs(_path)
    result = process_runner(["ellar", "new", "ellar-project-new", str(_path)])
    assert result.returncode == 0, result.stderr
    assert (
        "ellar --project ellar_project_new runserver --reload"
        in result.stdout.decode("utf8")
    )


def test_new_command_fails_case_1(tmpdir, process_runner):
    result = process_runner(["ellar", "new", "ellar-project-new", "Another/me"])
    assert result.returncode == 0, result.stderr
    result = process_runner(["ellar", "new", "ellar-project-new", "Another/me"])
    assert result.returncode == 1
    assert "Scaffolding Project Directory is not empty." in result.stderr.decode("utf8")


def test_new_command_works_with_specific_directory_case_2(tmpdir, process_runner):
    result = process_runner(["ellar", "new", "ellar-project-new", "."])
    assert result.returncode == 0, result.stderr
    assert result.stdout.decode("utf8") == (
        "`ellar_project_new` project created successfully.\n\n"
        "To start your server, run the command below\n"
        "- ellar --project ellar_project_new runserver --reload\n"
        "Happy coding!\n"
    )
    os.chdir(os.path.join(tmpdir))
    ellar_cli_service = EllarCLIService.import_project_meta()
    assert ellar_cli_service._meta.dict() == {
        "project_name": "ellar_project_new",
        "application": "ellar_project_new.server:application",
        "config": "ellar_project_new.config:DevelopmentConfig",
        "root_module": "ellar_project_new.root_module:ApplicationModule",
    }


# def test_new_command_fails_for_existing_folder_name(tmp_path, process_runner):
#     os.makedirs(tmp_path / "ellar-project-exist", exist_ok=True)
#     result = process_runner(["ellar", "new", "ellar-project-exist"])
#     assert result.returncode == 1
#     assert result.stderr.decode("utf8") == (
#         "Error: A folder with same name exist 'ellar-project-exist' \n"
#     )


def test_new_command_fails_for_invalid_project_name(tmp_path, process_runner):
    result = process_runner(["ellar", "new", "ellar-project-exist&^"])
    assert result.returncode == 1
    assert result.stderr.decode("utf8") == (
        "Error: 'ellar-project-exist&^' is not a valid project-name. "
        "Please make sure the project-name is a valid identifier.\n"
    )


def test_new_template_scaffold_get_project_name():
    init_template_scaffold = NewTemplateScaffold(
        schema=EllarScaffoldSchema.schema_example(),
        working_directory=os.getcwd(),
        scaffold_ellar_template_root_path="",
        project_name="folder-name".lower(),
    )
    assert init_template_scaffold.get_project_name() == "folder_name"
    init_template_scaffold._project_name = "folder-name!;-:*"
    assert init_template_scaffold.get_project_name() == "folder_name_____"
    assert init_template_scaffold.get_project_name().isidentifier()


def test_new_template_scaffold_get_project_cwd():
    init_template_scaffold = NewTemplateScaffold(
        schema=EllarScaffoldSchema.schema_example(),
        working_directory="working-directory",
        scaffold_ellar_template_root_path="",
        project_name="folder-name".lower(),
    )
    assert init_template_scaffold.get_project_cwd() == "working-directory/folder-name"
