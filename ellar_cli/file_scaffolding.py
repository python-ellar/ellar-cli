import os
import typing as t
from abc import abstractmethod
from pathlib import Path

from jinja2 import Environment

from ellar_cli.schema import EllarScaffoldList, EllarScaffoldSchema

__all__ = ["FileTemplateScaffold"]


class ProjectScaffoldContext(dict):
    def __init__(self, environment: Environment, **kwargs: t.Any) -> None:
        super().__init__(kwargs)
        self.environment = environment
        self.environment.globals.update(kwargs)


class FileTemplateScaffold:
    def __init__(
        self,
        *,
        schema: EllarScaffoldSchema,
        working_project_name: str,
        working_directory: str,
        scaffold_ellar_template_root_path: str,
        specified_directory: t.Optional[str] = None,
    ) -> None:
        self._specified_directory = specified_directory

        self._schema = schema
        self._ctx = ProjectScaffoldContext(Environment())
        self._scaffold_ellar_template_root_path = scaffold_ellar_template_root_path

        if self._specified_directory:
            _cwd_path = Path(self._get_working_cwd(working_directory))
            self._working_project_name = _cwd_path.name
            self._working_directory = str(_cwd_path.parent)
        else:
            self._working_directory = working_directory
            self._working_project_name = working_project_name

    def get_scaffolding_context(self, working_project_name: str) -> t.Dict:
        return {}

    @classmethod
    def read_file_content(cls, path: str) -> str:
        with open(path, mode="r") as fp:
            return fp.read()

    def create_root_path(self) -> str:
        root_dir = os.path.join(
            self._working_directory, self._working_project_name.lower()
        )
        os.mkdir(root_dir)
        return root_dir

    def create_file(self, base_path: str, file_name: str, content: t.Any) -> None:
        with open(
            os.path.join(base_path, file_name.replace(".ellar", ".py")), mode="w"
        ) as fw:
            refined_content = self._ctx.environment.from_string(content).render()
            fw.writelines(refined_content)

    def scaffold(self) -> None:
        self.validate_project_name()
        self._ctx = self.get_templating_context()
        self.on_scaffold_started()
        for file in self._schema.files:
            self.create_directory(
                file,
                scaffold_ellar_template_path=self._scaffold_ellar_template_root_path,
                working_directory=self._working_directory,
            )
        self.on_scaffold_completed()

    def on_scaffold_completed(self) -> None:
        pass

    def on_scaffold_started(self) -> None:
        for context in self._schema.context:
            assert (
                self._ctx.get(context) is not None
            ), f"{context} template context is missing."

    def create_directory(
        self,
        file: EllarScaffoldList,
        scaffold_ellar_template_path: str,
        working_directory: str,
    ) -> None:
        name = file.name
        if name in self._ctx:
            name = self._ctx.get(file.name, file.name)

        scaffold_template_path = os.path.join(scaffold_ellar_template_path, file.name)

        if file.is_directory:
            new_scaffold_dir = os.path.join(working_directory, name)
            os.makedirs(new_scaffold_dir, exist_ok=True)
            for _file in file.files:
                self.create_directory(
                    file=_file,
                    working_directory=new_scaffold_dir,
                    scaffold_ellar_template_path=scaffold_template_path,
                )
        else:
            content = self.read_file_content(scaffold_template_path)
            self.create_file(
                base_path=working_directory, file_name=name, content=content
            )

    @abstractmethod
    def validate_project_name(self) -> None:
        # Check it's a valid directory name.
        pass

    def _get_working_cwd(self, working_directory: str) -> str:
        if self._specified_directory:
            return self._handle_directory_change(working_directory)
        return working_directory

    def _handle_directory_change(self, working_directory: str) -> str:
        if self._specified_directory == ".":
            return working_directory

        _specified_directory = (
            self._specified_directory.lower()  # type:ignore[union-attr]
        )
        return os.path.join(str(working_directory), _specified_directory)

    def get_templating_context(self) -> ProjectScaffoldContext:
        return ProjectScaffoldContext(
            Environment(), **self.get_scaffolding_context(self._working_project_name)
        )
