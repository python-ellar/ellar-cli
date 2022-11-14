import os
import re
import subprocess
import typing as t

import typer
from ellar.helper.module_loading import module_dir

from ellar_cli import scaffolding
from ellar_cli.schema import EllarScaffoldSchema

from ..file_scaffolding import FileTemplateScaffold
from ..service import EllarCLIException

__all__ = ["new_command"]


conf_module_dir = module_dir(scaffolding)
root_scaffold_template_path = os.path.join(conf_module_dir, "new_template")
init_template_json = os.path.join(root_scaffold_template_path, "setup.json")


class NewTemplateScaffold(FileTemplateScaffold):
    unwanted_chars = "".join(["-", ";", "!", "*", ":", " "])

    def __init__(self, project_name: str = None, **kwargs: t.Any) -> None:
        self._project_name = project_name
        super(NewTemplateScaffold, self).__init__(**kwargs)

    def on_scaffold_completed(self) -> None:
        popen_res = subprocess.run(
            ["ellar", "create-project", self.get_project_name()],
            cwd=self.get_project_cwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if popen_res.returncode == 0:
            project_working_project_name = self.get_project_name()
            print(
                f"`{self._working_project_name}` project created successfully.\n"
                f"- cd {self._working_project_name}"
            )
            print("To start your server, run the command below")
            print(
                f"- ellar --project {project_working_project_name} runserver --reload\nHappy coding!"
            )
        else:
            print(popen_res.stderr.decode("utf8"))

    def validate_project_name(self) -> None:
        if os.path.exists(self._working_project_name):
            message = "A folder with same name exist '{name}' ".format(
                name=self._working_project_name
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
        template_context = dict(
            folder_name=working_project_name, project_name=self.get_project_name()
        )
        return template_context

    def get_project_name(self) -> str:
        project_working_project_name = self._project_name or self._working_project_name
        return re.sub(rf"[{self.unwanted_chars}]", "_", project_working_project_name)

    def get_project_cwd(self) -> str:
        return os.path.join(self._working_directory, self._working_project_name)


def new_command(
    folder_name: str,
    project_name: t.Optional[str] = typer.Option(
        None,
        help="Project Module Name. Defaults to `folder-name` if not set",
        show_default=False,
    ),
):
    """- Runs a complete Ellar project scaffold and creates all files required for managing you application  -"""
    schema = EllarScaffoldSchema.parse_file(init_template_json)
    init_template_scaffold = NewTemplateScaffold(
        schema=schema,
        working_directory=os.getcwd(),
        scaffold_ellar_template_root_path=root_scaffold_template_path,
        working_project_name=folder_name.lower(),
        project_name=project_name,
    )
    init_template_scaffold.scaffold()
