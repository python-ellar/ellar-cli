
This command helps you create ellar project module, like a small app within a project. 
It depends on the existence of an ellar project.

```shell
ellar create-module my_project_module
```

will create a folder as follows:
```angular2html
john_doe
├── apps
|   ├── my_project_module
|   |   └── __init__.py
|   |   └── controllers.py
|   |   └── module.py
|   |   └── routers.py
|   |   └── schemas.py
|   |   └── services.py
|   |   └── tests
|   └── __init__.py
├── core
├── domain
└── __init__.py
└── config.py
└── root_module.py
└── server.py
```
