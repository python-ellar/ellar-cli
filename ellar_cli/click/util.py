import typing as t
from functools import update_wrapper

import click
from ellar.threading.sync_worker import (
    execute_async_context_manager,
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
                execute_async_context_manager(meta_.get_application_context())
            )

        return __ctx.invoke(f, *args, **kwargs)

    return update_wrapper(decorator, f)
