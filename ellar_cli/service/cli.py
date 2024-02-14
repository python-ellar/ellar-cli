import asyncio
import functools
import os
import sys
import typing as t

from ellar.app import App
from ellar.app.context import ApplicationContext
from ellar.common.constants import ELLAR_CONFIG_MODULE
from ellar.core import Config, ModuleBase
from ellar.utils.importer import import_from_string, module_import
from tomlkit import dumps as tomlkit_dumps
from tomlkit import parse as tomlkit_parse
from tomlkit.items import Table

from ellar_cli.constants import ELLAR_PY_PROJECT
from ellar_cli.schema import EllarPyProjectSerializer, MetadataStore

from .exceptions import EllarCLIException
from .pyproject import PY_PROJECT_TOML, EllarPyProject


def _export_ellar_config_module(func: t.Callable) -> t.Callable:
    """Ensure Ellar Config Module is Exported"""

    @functools.wraps(func)
    def _wrap(self: "EllarCLIService", *args: t.Any, **kwargs: t.Any) -> t.Any:
        if (
            os.environ.get(ELLAR_CONFIG_MODULE) is None
            and self.has_meta
            and self._meta.config != "null"
        ):
            # export ELLAR_CONFIG_MODULE module
            os.environ.setdefault(
                ELLAR_CONFIG_MODULE,
                self._meta.config,
            )
        return func(self, *args, **kwargs)

    return _wrap


class EllarCLIService:
    schema_cls: t.Type[EllarPyProjectSerializer] = EllarPyProjectSerializer

    def __init__(
        self,
        *,
        meta: t.Optional[EllarPyProjectSerializer] = None,
        py_project_path: str,
        cwd: str,
        app_name: str = "ellar",
        ellar_py_projects: t.Optional[EllarPyProject] = None,
    ) -> None:
        self._meta = meta
        self._store: MetadataStore = MetadataStore(is_app_reference_callable=False)
        self.py_project_path = py_project_path
        self.cwd = cwd
        self.app = app_name
        self.ellar_py_projects = ellar_py_projects or EllarPyProject()

    @property
    def has_meta(self) -> bool:
        return self._meta is not None

    @property
    def project_meta(self) -> t.Optional[EllarPyProjectSerializer]:
        return self._meta

    @classmethod
    def cwd_has_pyproject_file(cls) -> bool:
        cwd = os.getcwd()
        py_project_file_path = os.path.join(cwd, PY_PROJECT_TOML)
        return os.path.exists(py_project_file_path)

    @classmethod
    def import_project_meta(
        cls, project: t.Optional[str] = None
    ) -> t.Optional["EllarCLIService"]:
        cwd = os.getcwd()
        project_to_load: str = "ellar"
        ellar_py_projects = None

        py_project_file_path = os.path.join(cwd, PY_PROJECT_TOML)
        if os.path.exists(py_project_file_path):
            pyproject_table = EllarCLIService.read_py_project(py_project_file_path)
            _ellar_pyproject_serializer: t.Optional[EllarPyProjectSerializer] = None

            if pyproject_table and ELLAR_PY_PROJECT in pyproject_table:
                ellar_py_projects = EllarPyProject(
                    pyproject_table.get(ELLAR_PY_PROJECT)
                )
                if ellar_py_projects.has_project(
                    project
                ) or ellar_py_projects.has_project(ellar_py_projects.default_project):
                    project_to_load = (
                        project  # type: ignore
                        if ellar_py_projects.has_project(project)
                        else ellar_py_projects.default_project
                    )

                    _ellar_pyproject_serializer = cls.schema_cls.model_validate(
                        ellar_py_projects.get_project(project_to_load)
                    )

            return cls(
                meta=_ellar_pyproject_serializer,
                py_project_path=py_project_file_path,
                cwd=cwd,
                app_name=project_to_load,
                ellar_py_projects=ellar_py_projects,
            )
        return None

    def create_ellar_project_meta(
        self, project_name: str, prefix: t.Optional[str] = None
    ) -> None:
        pyproject_table = EllarCLIService.read_py_project(self.py_project_path)
        if pyproject_table is None:
            raise EllarCLIException("Could not locate `pyproject.toml`")

        ellar_py_project = self.ellar_py_projects.get_or_create_ellar_py_project(
            pyproject_table
        )

        if ellar_py_project.has_project(project_name.lower()):
            raise EllarCLIException(
                f"project -> `{project_name}` already exist in ellar projects"
            )

        if not ellar_py_project.has_default_project:
            ellar_py_project.default_project = project_name.lower()

        _prefix = f"{prefix}." if prefix else ""

        ellar_new_project = ellar_py_project.get_or_create_project(project_name.lower())
        ellar_new_project.add("project-name", project_name.lower())
        ellar_new_project.add(
            "application", f"{_prefix}{project_name}.server:bootstrap"
        )
        ellar_new_project.add(
            "config", f"{_prefix}{project_name}.config:DevelopmentConfig"
        )
        ellar_new_project.add(
            "root-module", f"{_prefix}{project_name}.root_module:ApplicationModule"
        )

        # TODO: lock pyproject.toml file
        EllarCLIService.write_py_project(self.py_project_path, pyproject_table)

    @staticmethod
    def read_py_project(path: str) -> t.Optional[Table]:
        if os.path.exists(path):
            with open(path, mode="r") as fp:
                table_content = tomlkit_parse(fp.read())
                return table_content
        return None

    @staticmethod
    def write_py_project(path: str, content: Table) -> None:
        with open(path, mode="w") as fw:
            fw.writelines(tomlkit_dumps(content))

    def _import_from_string(self) -> t.Union[App, t.Callable[..., App]]:
        return import_from_string(self._meta.application)  # type:ignore[no-any-return]

    def _import_and_validate_application(
        self,
    ) -> None:
        assert self._meta
        app = self._import_from_string()
        is_callable = not isinstance(app, App)

        if is_callable and asyncio.iscoroutinefunction(app):
            raise EllarCLIException(
                "Coroutine Application Bootstrapping is not supported."
            )

        if is_callable:
            app = app()  # type:ignore[call-arg]

            if not isinstance(app, App):
                raise EllarCLIException(
                    "Boostrap Function must return Instance of `ellar.app.App` type"
                )

        self._store.app_instance = app
        self._store.is_app_reference_callable = is_callable
        self._store.config_instance = app.config

    @_export_ellar_config_module
    def import_application(self) -> App:
        assert self._meta
        if not self._store.app_instance:
            self._import_and_validate_application()

        assert isinstance(self._store.app_instance, App)
        return self._store.app_instance

    def is_app_callable(self) -> bool:
        if not self._store.is_app_reference_callable:
            self._import_and_validate_application()

        return self._store.is_app_reference_callable

    def import_configuration(self) -> t.Type["Config"]:
        assert self._meta
        if "Config" not in self._store:
            self._store["Config"] = t.cast(
                t.Type["Config"], import_from_string(self._meta.config)
            )
        return self._store["Config"]

    @_export_ellar_config_module
    def get_application_config(self) -> "Config":
        assert self._meta
        if not self._store.config_instance:  # pragma: no cover
            self._store.config_instance = Config(
                os.environ.get(ELLAR_CONFIG_MODULE, self._meta.config)
            )
        return self._store.config_instance

    @_export_ellar_config_module
    def import_root_module(self) -> t.Type["ModuleBase"]:
        assert self._meta
        if not self._store.root_module:
            self._store.root_module = t.cast(
                t.Type["ModuleBase"], import_from_string(self._meta.root_module)
            )
        return self._store.root_module

    @_export_ellar_config_module
    def get_application_context(self) -> ApplicationContext:
        app = t.cast(App, self.import_application())
        return app.application_context()


class EllarCLIServiceWithPyProject(EllarCLIService):
    def __init__(self, *, app_import_string: str) -> None:
        project_meta = EllarPyProjectSerializer.model_validate(
            {
                "project-name": "null",
                "application": app_import_string,
                "config": "null",
                "root-module": "null",
            },
            from_attributes=True,
        )
        super().__init__(meta=project_meta, py_project_path="null", cwd=os.getcwd())
        self.set_proper_sys_module_path()

    def set_proper_sys_module_path(self) -> None:
        assert self._meta
        module_str, _, attrs_str = self._meta.application.partition(":")
        module_path = module_str.replace(".", "/")

        path = os.path.realpath(module_path)

        if os.path.basename(path) == "__init__":
            path = os.path.dirname(path)

        module_name = []

        # move up until outside package structure (no __init__.py)
        while True:
            path, name = os.path.split(path)
            module_name.append(name)

            if not os.path.exists(os.path.join(path, "__init__.py")):
                break

        if sys.path[0] != path:
            sys.path.insert(0, path)

    def _import_from_string(self) -> t.Any:
        assert self._meta
        module_str, _, attrs_str = self._meta.application.partition(":")

        # start with __main__, in case infer module_str is the __main__ module
        module = sys.modules.get("__main__")

        if (
            module
            and module_str != "__main__"
            and not module.__file__.endswith(f"{module_str}.py")
        ):
            module = sys.modules.get(module_str)

        if not module:
            module = module_import(module_str)

        instance = module
        try:
            for attr_str in attrs_str.split("."):
                instance = getattr(module, attr_str)
        except AttributeError as attr_ex:
            message = (
                'Attribute "{attrs_str}" not found in python module "{module_file}".'
            )
            raise EllarCLIException(
                message.format(attrs_str=attrs_str, module_file=module.__file__)
            ) from attr_ex
        return instance

    def import_configuration(self) -> t.Type[Config]:
        raise EllarCLIException("Not Available")

    def get_application_config(self) -> Config:
        return self.import_application().config

    def import_root_module(self) -> t.Type[ModuleBase]:
        raise EllarCLIException("Not Available")
