import typing as t

from ellar.common.serializer import Serializer
from pydantic import Field


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


EllarScaffoldList.update_forward_refs()


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
