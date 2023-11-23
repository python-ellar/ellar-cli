import os


def test_create_module_fails_for_invalid_module_name(
    process_runner, write_empty_py_project
):
    result = process_runner(["ellar", "create-module", "testing-new-module"])
    assert result.returncode == 1
    assert result.stderr.decode("utf8") == (
        "Error: 'testing-new-module' is not a valid module-name. "
        "Please make sure the module-name is a valid identifier.\n"
    )


def test_create_module_with_directory_case_1(process_runner, tmpdir):
    result = process_runner(["ellar", "create-module", "test_new_module", "app/"])
    assert result.returncode == 0, result.stderr
    assert result.stdout == b"test_new_module module completely scaffolded\n"

    module_path = os.path.join(tmpdir, "app", "test_new_module")
    files = os.listdir(module_path)

    for file in [
        "module.py",
        "tests",
        "routers.py",
        "services.py",
        "controllers.py",
        "schemas.py",
        "__init__.py",
    ]:
        assert file in files


def test_create_module_with_directory_case_2(process_runner, tmpdir):
    result = process_runner(
        ["ellar", "create-module", "test_new_module", "."], cwd=tmpdir
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == b"test_new_module module completely scaffolded\n"

    files = os.listdir(tmpdir / "test_new_module")

    for file in [
        "module.py",
        "tests",
        "routers.py",
        "services.py",
        "controllers.py",
        "schemas.py",
        "__init__.py",
    ]:
        assert file in files


def test_create_module_fails_for_existing_module_project_name(
    process_runner, write_empty_py_project, tmp_path
):
    module_name = "new_module_name"
    with open(
        os.path.join(tmp_path, module_name + ".py"),
        mode="w",
    ) as fp:
        fp.write("")

    result = process_runner(
        ["ellar", "--project=testing_new_project_two", "create-module", module_name]
    )
    assert result.returncode == 1
    assert result.stderr.decode("utf8") == (
        "Error: 'new_module_name' conflicts with the name of an existing "
        "Python module and cannot be used as a module-name. Please try another module-name.\n"
    )


def test_create_module_fails_for_existing_directory_name(
    tmpdir, process_runner, write_empty_py_project
):
    module_name = "new_module_the_same_directory_name"
    os.makedirs(
        os.path.join(tmpdir, module_name),
        exist_ok=True,
    )

    result = process_runner(
        ["ellar", "--project=testing_new_project_three", "create-module", module_name]
    )
    assert result.returncode == 1
    assert result.stderr.decode("utf8") == (
        "Error: 'new_module_the_same_directory_name' conflicts with the name of an existing "
        "Python module and cannot be used as a module-name. Please try another module-name.\n"
    )


def test_create_module_works(tmpdir, process_runner, write_empty_py_project):
    result = process_runner(
        [
            "ellar",
            "--project=test_project_new_module",
            "create-module",
            "test_new_module",
        ]
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == b"test_new_module module completely scaffolded\n"

    module_path = os.path.join(tmpdir, "test_new_module")
    files = os.listdir(module_path)

    for file in [
        "module.py",
        "tests",
        "routers.py",
        "services.py",
        "controllers.py",
        "schemas.py",
        "__init__.py",
    ]:
        assert file in files

    module_test_path = os.path.join(tmpdir, "test_new_module", "tests")
    test_files = os.listdir(module_test_path)
    for file in ["test_routers.py", "test_services.py", "test_controllers.py"]:
        assert file in test_files
