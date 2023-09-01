from ellar.common import JSONResponse, Module, Response, exception_handler
from ellar.core import ModuleBase
from ellar.core.connection import Request

from .commands import db, say_hello, whatever_you_want


@Module(commands=[db, whatever_you_want, say_hello])
class ApplicationModule(ModuleBase):
    @exception_handler(404)
    def exception_404_handler(cls, request: Request, exc: Exception) -> Response:
        return JSONResponse({"detail": "Resource not found."})
