import inspect
import typing as t

import click
from ellar.app import AppFactory
from ellar.common.constants import MODULE_METADATA
from ellar.core import ModuleBase, ModuleSetup, reflector
from ellar.threading import run_as_sync

from ellar_cli.constants import ELLAR_META
from ellar_cli.service import EllarCLIService, EllarCLIServiceWithPyProject

from .command import Command
from .util import with_injector_context


class AppContextGroup(click.Group):
    """This works similar to a regular click.Group, but it
    changes the behavior of the command decorator so that it
    automatically wraps the functions in `with_injector_context`.
    """

    command_class = Command

    def command(  # type:ignore[override]
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Union[t.Callable[[t.Callable[..., t.Any]], click.Command], click.Command]:
        """The same with click.Group command.
        It only decorates the command function to be run under `ellar.core.with_injector_context`.
        It's disabled by passing `with_injector_context=False`.
        """
        wrap_for_ctx = kwargs.pop("with_injector_context", True)

        def decorator(f: t.Callable) -> t.Any:
            if inspect.iscoroutinefunction(f):
                f = run_as_sync(f)

            if wrap_for_ctx:
                f = with_injector_context(f)
            return super(AppContextGroup, self).command(*args, **kwargs)(f)

        return decorator

    def group(  # type:ignore[override]
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Union[t.Callable[[t.Callable[..., t.Any]], click.Group], click.Group]:
        """This works exactly like the method of the same name on a regular click.Group but it defaults
        the group class to `AppGroup`.
        """
        kwargs.setdefault("cls", self.__class__)
        return super(AppContextGroup, self).group(*args, **kwargs)  # type:ignore[no-any-return]


class EllarCommandGroup(AppContextGroup):
    """Overrides AppContextGroup to add loading of Ellar Application registered commands in the modules"""

    def __init__(
        self, app_import_string: t.Optional[str] = None, **kwargs: t.Any
    ) -> None:
        super().__init__(**kwargs)
        meta = None

        if app_import_string:
            meta = EllarCLIServiceWithPyProject(app_import_string=app_import_string)

        self._cli_meta: t.Optional[EllarCLIServiceWithPyProject] = meta

    def _load_application_commands(self, ctx: click.Context) -> None:
        # get project option from cli
        module_configs: t.Any
        if self._cli_meta:
            application = self._cli_meta.import_application()

            module_configs = (
                i for i in application.injector.tree_manager.modules.keys()
            )

            ctx.meta[ELLAR_META] = self._cli_meta
        else:
            module_configs = ()
            app_name = ctx.params.get("project")

            # loads project metadata from pyproject.toml
            meta_: t.Optional[EllarCLIService] = EllarCLIService.import_project_meta(
                app_name
            )

            ctx.meta[ELLAR_META] = meta_

            if meta_ and meta_.has_meta:
                tree_manager = AppFactory.read_all_module(
                    ModuleSetup(meta_.import_root_module())
                )
                module_configs = tree_manager.modules.keys()
        self._find_commands_from_modules(module_configs)

    def _find_commands_from_modules(
        self,
        modules: t.Union[t.Sequence[ModuleBase], t.Iterator[ModuleBase], t.Generator],
    ) -> None:
        for module in modules:
            click_commands = reflector.get(MODULE_METADATA.COMMANDS, module) or []

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
