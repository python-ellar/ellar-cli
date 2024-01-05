import typing as t

import click
from ellar.app import AppFactory
from ellar.common.constants import MODULE_METADATA
from ellar.core import ModuleSetup, reflector

from ellar_cli.constants import ELLAR_META
from ellar_cli.service import EllarCLIService

from .command import Command
from .util import with_app_context


class AppContextGroup(click.Group):
    """This works similar to a regular click.Group, but it
    changes the behavior of the command decorator so that it
    automatically wraps the functions in `pass_with_app_context`.
    """

    command_class = Command

    def command(self, *args: t.Any, **kwargs: t.Any) -> t.Callable:  # type:ignore[override]
        """The same with click.Group command.
        It only decorates the command function to be run under `applicationContext`.
        It's disabled by passing `with_app_context=False`.
        """
        wrap_for_ctx = kwargs.pop("with_app_context", True)

        def decorator(f: t.Callable) -> t.Any:
            if wrap_for_ctx:
                f = with_app_context(f)
            return click.Group.command(self, *args, **kwargs)(f)

        return decorator

    def group(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        """This works exactly like the method of the same name on a regular click.Group but it defaults
        the group class to `AppGroup`.
        """
        kwargs.setdefault("cls", AppContextGroup)
        return click.Group.group(self, *args, **kwargs)


class EllarCommandGroup(AppContextGroup):
    """Overrides AppContextGroup to add loading of Ellar Application registered commands in the modules"""

    def _load_application_commands(self, ctx: click.Context) -> None:
        # get project option from cli
        app_name = ctx.params.get("project")

        # loads project metadata from pyproject.toml
        meta_: t.Optional[EllarCLIService] = EllarCLIService.import_project_meta(
            app_name
        )
        ctx.meta[ELLAR_META] = meta_

        if meta_ and meta_.has_meta:
            module_configs = AppFactory.get_all_modules(
                ModuleSetup(meta_.import_root_module())
            )

            for module_config in module_configs:
                click_commands = (
                    reflector.get(MODULE_METADATA.COMMANDS, module_config.module) or []
                )

                for click_command in click_commands:
                    if isinstance(click_command, click.Command):
                        self.add_command(click_command, click_command.name)

    def get_command(
        self, ctx: click.Context, cmd_name: str
    ) -> t.Optional[click.Command]:
        if ELLAR_META not in ctx.meta:
            self._load_application_commands(ctx)
        return super().get_command(ctx, cmd_name)

    def list_commands(self, ctx: click.Context) -> t.List[str]:
        if ELLAR_META not in ctx.meta:
            self._load_application_commands(ctx)
        return super().list_commands(ctx)
