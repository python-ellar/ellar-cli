from ellar.common import (
    IExecutionContext,
    IModuleSetup,
    JSONResponse,
    Module,
    Response,
    exception_handler,
)
from ellar.core import Config, DynamicModule, ModuleBase, current_injector
from ellar.samples.modules import HomeModule

import ellar_cli.click as click


@Module()
class DynamicCommandModule(ModuleBase, IModuleSetup):
    @classmethod
    def setup(cls) -> "DynamicModule":
        @click.command()
        @click.with_injector_context
        def plain_project():
            """Project 2 Custom Command"""
            assert isinstance(current_injector.get(Config), Config)
            print("Plain Project Command works. Executed within application context")

        return DynamicModule(cls, commands=[plain_project])


@Module(modules=[HomeModule, DynamicCommandModule.setup()])
class ApplicationModule(ModuleBase):
    @exception_handler(404)
    def exception_404_handler(cls, ctx: IExecutionContext, exc: Exception) -> Response:
        return JSONResponse({"detail": "Resource not found."}, status_code=404)
