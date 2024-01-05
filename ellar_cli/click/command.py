import typing as t

import click


class Command(click.Command):
    """
    The same as click.Command with extra behavior to print command args and options
    """

    # overridden to support displaying args before the options metavar
    def collect_usage_pieces(self, ctx: click.Context) -> t.List[str]:
        rv: t.List[str] = []
        for param in self.get_params(ctx):
            rv.extend(param.get_usage_pieces(ctx))

        rv.append(self.options_metavar)  # type:ignore[arg-type]
        return rv

    # overridden to group arguments separately from options
    def format_options(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        args, opts = [], []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                if isinstance(param, click.Argument):
                    args.append(rv)
                else:
                    opts.append(rv)

        def print_args() -> None:
            if args:
                with formatter.section("Arguments".upper()):
                    formatter.write_dl(args)

        def print_opts() -> None:
            if opts:
                with formatter.section(self.options_metavar):  # type:ignore[arg-type]
                    formatter.write_dl(opts)

        print_args()
        print_opts()
