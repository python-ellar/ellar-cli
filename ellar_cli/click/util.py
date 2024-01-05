import asyncio
import typing as t
from functools import update_wrapper

import click
from ellar.threading import execute_coroutine_with_sync_worker

from ellar_cli.constants import ELLAR_META
from ellar_cli.service import EllarCLIService


def _async_run(future: t.Coroutine) -> t.Any:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # no event loop running:
        loop = asyncio.new_event_loop()

    if not loop.is_running():
        try:
            res = loop.run_until_complete(loop.create_task(future))
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception as e:
            raise e
        finally:
            loop.stop()
            loop.close()
    else:
        res = execute_coroutine_with_sync_worker(future)

    return res


def with_app_context(f: t.Callable) -> t.Any:
    """
    Wraps a callback so that it's guaranteed to be executed with application context.
    Also, wrap commands can be a coroutine.
    """

    async def _run_with_application_context(
        meta_: t.Optional[EllarCLIService], *args: t.Any, **kwargs: t.Any
    ) -> t.Any:
        if meta_ and meta_.has_meta:
            async with meta_.get_application_context():
                res = f(*args, **kwargs)
                if isinstance(res, t.Coroutine):
                    return await res
                return res

        res = f(*args, **kwargs)
        if isinstance(res, t.Coroutine):
            return await res

    @click.pass_context
    def decorator(__ctx: click.Context, *args: t.Any, **kwargs: t.Any) -> t.Any:
        meta_ = __ctx.meta.get(ELLAR_META)

        def _get_command_args(*ar: t.Any, **kw: t.Any) -> t.Any:
            return _async_run(_run_with_application_context(meta_, *ar, **kw))

        return __ctx.invoke(update_wrapper(_get_command_args, f), *args, **kwargs)

    return update_wrapper(decorator, f)
