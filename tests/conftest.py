import os.path
import subprocess
import sys
from uuid import uuid4

import pytest
from tomlkit import table

from ellar_cli.service import PY_PROJECT_TOML, EllarCLIService, EllarPyProject
from ellar_cli.testing import EllarCliRunner


@pytest.fixture
def random_type():
    return type(f"Random{uuid4().hex[:6]}", (), {})


@pytest.fixture
def mock_py_project_table():
    return table()


@pytest.fixture
def ellar_py_project(mock_py_project_table):
    return EllarPyProject.get_or_create_ellar_py_project(mock_py_project_table)


@pytest.fixture
def add_ellar_project_to_py_project(ellar_py_project, tmp_py_project_path, tmp_path):
    EllarCLIService.write_py_project(
        tmp_py_project_path, ellar_py_project.get_root_node()
    )

    def _wrapper(project_name: str):
        cli_service = EllarCLIService(
            py_project_path=tmp_py_project_path,
            ellar_py_projects=ellar_py_project,
            cwd=str(tmp_path),
        )
        cli_service.create_ellar_project_meta(project_name)
        return ellar_py_project

    return _wrapper


@pytest.fixture
def write_empty_py_project(tmp_py_project_path, mock_py_project_table):
    EllarCLIService.write_py_project(tmp_py_project_path, mock_py_project_table)
    return mock_py_project_table


@pytest.fixture
def tmp_py_project_path(tmp_path):
    os.chdir(str(tmp_path))
    py_project_toml = tmp_path / PY_PROJECT_TOML
    py_project_toml.touch(exist_ok=True)
    return py_project_toml


@pytest.fixture(autouse=True)
def sys_path(tmp_path):
    sys.path.append(str(tmp_path))
    yield
    sys.path.remove(str(tmp_path))


@pytest.fixture
def cli_runner(tmp_path):
    os.chdir(str(tmp_path))
    return EllarCliRunner()


@pytest.fixture
def process_runner(tmp_path):
    os.chdir(str(tmp_path))

    def _wrapper_process(*args, **kwargs):
        kwargs.setdefault("stdout", subprocess.PIPE)
        kwargs.setdefault("stderr", subprocess.PIPE)
        result = subprocess.run(*args, **kwargs)
        return result

    return _wrapper_process
