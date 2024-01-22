from ellar.app import current_app
from ellar.common import (
    IExecutionContext,
    JSONResponse,
    Module,
    Response,
    exception_handler,
)
from ellar.core import Config, ModuleBase
from ellar.samples.modules import HomeModule

import ellar_cli.click as click


@click.command()
@click.with_app_context
def plain_project():
    """Project 2 Custom Command"""
    assert isinstance(current_app.config, Config)
    print("Plain Project Command works. Executed within application context")


@Module(modules=[HomeModule], commands=[plain_project])
class ApplicationModule(ModuleBase):
    @exception_handler(404)
    def exception_404_handler(cls, ctx: IExecutionContext, exc: Exception) -> Response:
        return JSONResponse({"detail": "Resource not found."}, status_code=404)
