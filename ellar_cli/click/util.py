import asyncio
import functools
import typing as t
from functools import update_wrapper

import click
from ellar.threading.sync_worker import (
    execute_async_context_manager_with_sync_worker,
    execute_coroutine_with_sync_worker,
)

from ellar_cli.constants import ELLAR_META
from ellar_cli.service import EllarCLIService


def with_app_context(f: t.Callable) -> t.Any:
    """
    Wraps a callback so that it's guaranteed to be executed with application context.
    """

    @click.pass_context
    def decorator(__ctx: click.Context, *args: t.Any, **kwargs: t.Any) -> t.Any:
        meta_: t.Optional[EllarCLIService] = __ctx.meta.get(ELLAR_META)

        if meta_ and meta_.has_meta:
            __ctx.with_resource(
                execute_async_context_manager_with_sync_worker(
                    meta_.get_application_context()
                )
            )

        return __ctx.invoke(f, *args, **kwargs)

    return update_wrapper(decorator, f)


def run_as_async(f: t.Callable) -> t.Callable:
    """
    Runs async click commands

    eg:

    @click.command()
    @click.argument('name')
    @click.run_as_async
    async def print_name(name: str):
        click.echo(f'Hello {name}, this is an async command.')
    """
    assert asyncio.iscoroutinefunction(f), "Decorated function must be Coroutine"

    @functools.wraps(f)
    def _decorator(*args: t.Any, **kw: t.Any) -> t.Any:
        return execute_coroutine_with_sync_worker(f(*args, **kw))

    return _decorator
