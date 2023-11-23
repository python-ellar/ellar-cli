import os
import secrets
import typing as t
from importlib import import_module
from pathlib import Path

import typer
from ellar.common.utils.module_loading import module_dir

from ellar_cli import scaffolding
from ellar_cli.constants import ELLAR_META
from ellar_cli.schema import EllarScaffoldSchema

from ..file_scaffolding import FileTemplateScaffold
from ..service import EllarCLIException, EllarCLIService

__all__ = ["create_project"]


conf_module_dir = module_dir(scaffolding)
root_scaffold_template_path = os.path.join(conf_module_dir, "project_template")
project_template_json = os.path.join(root_scaffold_template_path, "setup.json")


class ProjectTemplateScaffold(FileTemplateScaffold):
    def __init__(
        self,
        ellar_cli_service: EllarCLIService,
        working_project_name: str,
        working_directory: str,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(
            **kwargs,
            working_project_name=working_project_name,
            working_directory=working_directory,
        )
        self.ellar_cli_service = ellar_cli_service
        self._working_project_name = working_project_name
        if self._specified_directory:
            _cwd_path = Path(self._get_working_cwd(working_directory))
            self._working_directory = str(_cwd_path)
        else:
            self._working_directory = working_directory

        self.prefix: t.Optional[str] = None
        if self._specified_directory and "." not in self._specified_directory:
            self.prefix = self._specified_directory.replace("/", ".").lower()

            if self.prefix.startswith("."):  # pragma: no cover
                self.prefix = self.prefix[1:]

            if self.prefix.endswith("."):  # pragma: no cover
                self.prefix = self.prefix[:-1]

    def get_scaffolding_context(self, working_project_name: str) -> t.Dict:
        _prefix = f"{self.prefix}." if self.prefix else ""
        template_context = {
            "project_name": working_project_name,
            "secret_key": f"ellar_{secrets.token_urlsafe(32)}",
            "config_prefix": _prefix,
        }
        return template_context

    def validate_project_name(self) -> None:
        if not self._working_project_name.isidentifier():
            message = (
                "'{name}' is not a valid project-name. "
                "Please make sure the project-name is a valid identifier.".format(
                    name=self._working_project_name
                )
            )
            raise EllarCLIException(message)
        # Check it cannot be imported.
        try:
            xyz = import_module(self._working_project_name)
            if not xyz.__spec__.origin:
                # proceed
                raise ImportError()
        except ImportError:
            pass
        else:
            message = (
                "'{name}' conflicts with the name of an existing Python "
                "module and cannot be used as a project-name. Please try another project-name.".format(
                    name=self._working_project_name
                )
            )
            raise EllarCLIException(message)

    def on_scaffold_completed(self) -> None:
        _working_project_name = self._working_project_name

        self.ellar_cli_service.create_ellar_project_meta(
            project_name=_working_project_name, prefix=self.prefix
        )
        print(
            f"`{self._working_project_name}` project scaffold completed. To start your server, run the command below"
        )
        print(f"ellar --project {self._working_project_name} runserver --reload")
        print("Happy coding!")


def create_project(
    ctx: typer.Context,
    project_name: str,
    directory: t.Optional[str] = typer.Argument(
        None,
        help="The name of a new directory to scaffold the project into.",
        show_default=False,
    ),
):
    """- Scaffolds Ellar Application -"""

    ellar_project_meta = t.cast(t.Optional[EllarCLIService], ctx.meta.get(ELLAR_META))
    if not ellar_project_meta:
        raise EllarCLIException("No pyproject.toml file found.")

    if ellar_project_meta.ellar_py_projects.has_project(project_name):
        raise EllarCLIException("Ellar Project already exist.")

    schema = EllarScaffoldSchema.parse_file(project_template_json)
    project_template_scaffold = ProjectTemplateScaffold(
        schema=schema,
        working_directory=os.getcwd(),
        scaffold_ellar_template_root_path=root_scaffold_template_path,
        ellar_cli_service=ellar_project_meta,
        specified_directory=directory,
        working_project_name=project_name.lower(),
    )
    project_template_scaffold.scaffold()
