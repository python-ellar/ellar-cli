
This command will help you kickstart your new Ellar project by creating a new project with a directory structure and other required files necessary for ellar to properly manage your project.

```shell
ellar new my-project
```

will create a folder as follows:
```angular2html
my-package
├── pyproject.toml
├── README.md
├── my_project
|    ├── apps
|    |   └── __init__.py
|    ├── core
|    ├── domain
|    └── __init__.py
|    └── config.py
|    └── root_module.py
|    └── server.py
└── tests
    └── __init__.py
```
If you want to name your project differently than the folder, you can pass the `--project-name` option:

```shell
ellar new my-project --project-name john-doe
```
will create a folder as follows:
```angular2html
my-package
├── pyproject.toml
├── README.md
├── john_doe
|    ├── apps
|    |   └── __init__.py
|    ├── core
|    ├── domain
|    └── __init__.py
|    └── config.py
|    └── root_module.py
|    └── server.py
└── tests
    └── __init__.py
```

### New Command CLI Options
- `--project-name` Set the resulting project module name. Defaults to folder-name is not provided.
