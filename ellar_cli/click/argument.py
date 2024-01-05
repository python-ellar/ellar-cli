import inspect as _inspect
import typing as t

import click
from click.formatting import join_options as _join_options


class Argument(click.Argument):
    """
    Regular click.Argument with extra formatting for printing command arguments
    """

    def __init__(
        self,
        param_decls: t.Sequence[str],
        required: t.Optional[bool] = None,
        help: t.Optional[str] = None,
        hidden: t.Optional[bool] = None,
        **attrs: t.Any,
    ) -> None:
        super().__init__(param_decls, required=required, **attrs)
        self.help = help
        self.hidden = hidden

    # overridden to customize the automatic formatting of metavars
    def make_metavar(self) -> str:
        if self.metavar is not None:
            return self.metavar
        var = "" if self.required else "["
        var += "<" + self.name + ">"  # type:ignore[operator]
        if self.nargs != 1:
            var += ", ..."
        if not self.required:
            var += "]"
        return var

    # this code is 90% copied from click.Option.get_help_record
    def get_help_record(self, ctx: click.Context) -> t.Optional[t.Tuple[str, str]]:
        any_prefix_is_slash: t.List[bool] = []

        if self.hidden:
            # TODO: test
            return None

        def _write_opts(opts: t.Any) -> str:
            rv, any_slashes = _join_options(opts)
            if any_slashes:
                # TODO: test
                any_prefix_is_slash[:] = [True]
            rv += ": " + self.make_metavar()
            return rv

        rv = [_write_opts(self.opts)]
        if self.secondary_opts:
            # TODO: test
            rv.append(_write_opts(self.secondary_opts))

        help_ = self.help or ""
        extra = []

        if self.default is not None:
            if isinstance(self.default, (list, tuple)):
                # TODO: test
                default_string = ", ".join("%s" % d for d in self.default)
            elif _inspect.isfunction(self.default):
                # TODO: test
                default_string = "(dynamic)"
            else:
                default_string = self.default  # type:ignore[assignment]
            extra.append("default: {}".format(default_string))

        if self.required:
            extra.append("required")
        if extra:
            help_ = "%s[%s]" % (help_ and help_ + "  " or "", "; ".join(extra))

        return (any_prefix_is_slash and "; " or " / ").join(rv), help_
