import os
import re
import subprocess
import typing as t

from ellar.utils.module_loading import module_dir

import ellar_cli.click as eClick
from ellar_cli import scaffolding
from ellar_cli.schema import EllarScaffoldSchema

from ..file_scaffolding import FileTemplateScaffold
from ..service import EllarCLIException

__all__ = ["new_command"]


conf_module_dir = module_dir(scaffolding)
new_template_template_path = os.path.join(conf_module_dir, "new_template")
new_manage_template_template_path = os.path.join(conf_module_dir, "new_manage_template")


class NewTemplateScaffold(FileTemplateScaffold):
    unwanted_chars = "".join(["-", ";", "!", "*", ":", " "])

    def __init__(
        self, project_name: str = None, pyproject_enabled: bool = True, **kwargs: t.Any
    ) -> None:
        super(NewTemplateScaffold, self).__init__(
            working_project_name=project_name, **kwargs
        )
        self._project_name = project_name
        self._pyproject_enabled = pyproject_enabled

    def create_file(self, base_path: str, file_name: str, content: t.Any) -> None:
        _path = os.path.join(base_path, file_name.replace(".ellar", ".py"))
        if os.path.exists(_path):  # pragma: no cover
            # if there is a context existing, we override the intended content with the existing context
            content = self.read_file_content(path=_path)

        with open(
            os.path.join(base_path, file_name.replace(".ellar", ".py")), mode="w"
        ) as fw:
            refined_content = self._ctx.environment.from_string(content).render()
            fw.writelines(refined_content)

    def on_scaffold_completed(self) -> None:
        args = ["ellar", "create-project", self.get_project_name()]
        if self._pyproject_enabled:
            args.append("--plain")

        popen_res = subprocess.run(
            args,
            cwd=self.get_project_cwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if popen_res.returncode == 0:
            project_working_project_name = self.get_project_name()

            log_1 = f"- cd {self._working_project_name}"
            if self._specified_directory:
                log_1 = (
                    f"- cd {self._specified_directory.lower()}"
                    if self._specified_directory != "."
                    else ""
                )

            print(
                f"`{project_working_project_name}` project created successfully.\n"
                f"{log_1}"
            )
            print("To start your server, run the command below")
            if self._pyproject_enabled:
                print("- python manage.py runserver --reload\nHappy coding!")
            else:
                print(
                    f"- ellar --project {project_working_project_name} runserver --reload\nHappy coding!"
                )

        else:  # pragma: no cover
            print(popen_res.stderr.decode("utf8"))

    def is_directory_empty(self) -> bool:
        """
        Check if the given directory is empty.
        """
        # Get the list of files and directories in the directory
        working_project_dir = os.path.join(
            self._working_directory, self._working_project_name
        )
        if os.path.isdir(working_project_dir):
            items = os.listdir(working_project_dir)
            exclude = ["poetry.lock", "pyproject.toml"]
            items = [item for item in items if item not in exclude]
            return len(items) == 0
        return True

    def validate_project_name(self) -> None:
        if not self.is_directory_empty():
            working_project_dir = os.path.join(
                self._working_directory, self._working_project_name
            )
            message = (
                f"Scaffolding Project Directory is not empty. - {working_project_dir}"
            )
            raise EllarCLIException(message)

        project_working_project_name = self.get_project_name()
        if not project_working_project_name.isidentifier():
            message = (
                "'{name}' is not a valid project-name. "
                "Please make sure the project-name "
                "is a valid identifier.".format(name=self._working_project_name)
            )
            raise EllarCLIException(message)

    def get_scaffolding_context(self, working_project_name: str) -> t.Dict:
        template_context = {
            "folder_name": working_project_name,
            "project_name": self.get_project_name(),
        }
        return template_context

    def get_project_name(self) -> str:
        project_working_project_name = self._project_name or self._working_project_name
        return re.sub(rf"[{self.unwanted_chars}]", "_", project_working_project_name)

    def get_project_cwd(self) -> str:
        return os.path.join(self._working_directory, self._working_project_name)


@eClick.argument(
    "project_name",
    help="Project Module Name. Defaults to `project-name` if not set",
)
@eClick.argument(
    "directory",
    required=False,
    help="The name of a new directory to scaffold the project into. Scaffolding into an existing directory is only allowed if the directory is empty",
)
@eClick.option(
    "--plain",
    is_flag=True,
    default=False,
    help="Create a new without including `pyproject.toml`.",
)
def new_command(project_name: str, directory: t.Optional[str], plain: bool):
    """- Runs a complete Ellar project scaffold and creates all files required for managing you application  -"""
    root_scaffold_template_path = new_template_template_path
    init_template_json = os.path.join(root_scaffold_template_path, "setup.json")

    if plain:
        root_scaffold_template_path = new_manage_template_template_path
        init_template_json = os.path.join(root_scaffold_template_path, "setup.json")

    schema = EllarScaffoldSchema.parse_file(init_template_json)
    init_template_scaffold = NewTemplateScaffold(
        schema=schema,
        working_directory=os.getcwd(),
        scaffold_ellar_template_root_path=root_scaffold_template_path,
        project_name=project_name,
        specified_directory=directory,
        pyproject_enabled=plain,
    )
    init_template_scaffold.scaffold()
