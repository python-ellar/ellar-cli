import os
import sys
import typing as t
from importlib import import_module
from pathlib import Path

import typer
from ellar.common.utils.module_loading import module_dir

from ellar_cli import scaffolding
from ellar_cli.schema import EllarScaffoldSchema

from ..file_scaffolding import FileTemplateScaffold
from ..service import EllarCLIException

__all__ = ["create_module"]

conf_module_dir = module_dir(scaffolding)
root_scaffold_template_path = os.path.join(conf_module_dir, "module_template")
module_template_json = os.path.join(root_scaffold_template_path, "setup.json")


class ModuleTemplateScaffold(FileTemplateScaffold):
    def __init__(
        self, working_project_name: str, working_directory: str, **kwargs: t.Any
    ) -> None:
        super().__init__(
            working_project_name=working_project_name,
            working_directory=working_directory,
            **kwargs,
        )
        if self._specified_directory:
            _cwd_path = Path(self._get_working_cwd(working_directory))
            self._working_project_name = working_project_name
            self._working_directory = str(_cwd_path)

    def on_scaffold_completed(self) -> None:
        print(f"{self._working_project_name} module completely scaffolded")

    def validate_project_name(self) -> None:
        working_directory_in_sys_path = False
        if self._working_directory in sys.path:
            working_directory_in_sys_path = True

        if not self._working_project_name.isidentifier():
            message = (
                f"'{self._working_project_name}' is not a valid module-name. "
                f"Please make sure the module-name is a valid identifier."
            )
            raise EllarCLIException(message)

        try:
            if not working_directory_in_sys_path:
                sys.path.append(self._working_directory)
            import_module(self._working_project_name)
        except ImportError:
            pass
        else:
            message = (
                "'{name}' conflicts with the name of an existing Python "
                "module and cannot be used as a module-name. Please try another module-name.".format(
                    name=self._working_project_name
                )
            )
            raise EllarCLIException(message)
        finally:
            if not working_directory_in_sys_path:
                sys.path.remove(self._working_directory)

    def get_scaffolding_context(self, working_project_name: str) -> t.Dict:
        template_context = {"module_name": working_project_name}
        return template_context


def create_module(
    module_name: str,
    directory: t.Optional[str] = typer.Argument(
        None,
        help="The name of a new directory to scaffold the module into.",
        show_default=False,
    ),
):
    """- Scaffolds Ellar Application Module -"""

    schema = EllarScaffoldSchema.parse_file(module_template_json)
    project_template_scaffold = ModuleTemplateScaffold(
        schema=schema,
        working_directory=os.getcwd(),
        scaffold_ellar_template_root_path=root_scaffold_template_path,
        specified_directory=directory,
        working_project_name=module_name.lower(),
    )
    project_template_scaffold.scaffold()
