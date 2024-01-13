import typing as t

from ellar.app import App
from ellar.common.compatible import AttributeDict
from ellar.common.serializer import Serializer
from ellar.core import ModuleBase
from ellar.pydantic import Field


class MetadataStore(AttributeDict):
    app_instance: t.Optional[App]
    config_instance: t.Optional[App]
    is_app_reference_callable: bool
    root_module: t.Type[ModuleBase]

    def __missing__(self, name) -> None:
        return None


class EllarPyProjectSerializer(Serializer):
    project_name: str = Field(alias="project-name")
    application: str = Field(alias="application")
    config: str = Field(alias="config")
    root_module: str = Field(alias="root-module")


class EllarScaffoldList(Serializer):
    name: str
    is_directory: bool = False
    name_in_context: t.Optional[bool] = Field(default=None, alias="name-context")
    files: t.List["EllarScaffoldList"] = Field(default=[])


class EllarScaffoldSchema(Serializer):
    context: t.List[str]
    files: t.List[EllarScaffoldList]

    @classmethod
    def schema_example(cls) -> "EllarScaffoldSchema":
        return cls(
            context=["project_name"],
            files=[
                {"name": "sample.ellar", "is_directory": False},
                {
                    "name": "sample",
                    "files": [{"name": "sample.ellar", "is_directory": False}],
                },
            ],
        )


EllarScaffoldList.model_rebuild()
