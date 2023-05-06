from ellar.common import JSONResponse, Module, Response, exception_handler
from ellar.core import ModuleBase
from ellar.core.connection import Request

from .commands import db, whatever_you_want


@Module(commands=[db, whatever_you_want])
class ApplicationModule(ModuleBase):
    @exception_handler(404)
    def exception_404_handler(cls, request: Request, exc: Exception) -> Response:
        return JSONResponse(dict(detail="Resource not found."))
