import typing as t

from tomlkit import table
from tomlkit.items import Table

from ellar_cli.constants import ELLAR_PY_PROJECT

PY_PROJECT_TOML = "pyproject.toml"
ELLAR_DEFAULT_KEY = "default"
ELLAR_PROJECTS_KEY = "projects"


class EllarPyProject:
    def __init__(self, ellar: t.Optional[Table] = None) -> None:
        self._ellar = ellar if ellar is not None else table()
        self._projects = t.cast(
            Table, self._ellar.setdefault(ELLAR_PROJECTS_KEY, table())
        )
        self._default_project = self._ellar.get(ELLAR_DEFAULT_KEY, None)

    @classmethod
    def get_or_create_ellar_py_project(
        cls, py_project_table: Table
    ) -> "EllarPyProject":
        ellar_py_project_table = py_project_table.setdefault(ELLAR_PY_PROJECT, table())
        return cls(ellar_py_project_table)

    @property
    def has_default_project(self) -> bool:
        return self._ellar.get(ELLAR_DEFAULT_KEY, None) is not None

    @property
    def default_project(self) -> t.Optional[str]:
        return self._ellar.get(ELLAR_DEFAULT_KEY) or None

    @default_project.setter
    def default_project(self, value: str) -> None:
        self._ellar.update(default=value)

    def get_projects(self) -> Table:
        return self._projects

    def get_project(self, project_name: str) -> Table:
        return t.cast(Table, self._projects.get(project_name))

    def get_or_create_project(self, project_name: str) -> Table:
        project = self._projects.setdefault(project_name.lower(), table())
        return t.cast(Table, project)

    def has_project(self, project_name: t.Optional[str]) -> bool:
        if not project_name:
            return False
        return project_name in self._projects

    def get_root_node(self) -> Table:
        return self._ellar
