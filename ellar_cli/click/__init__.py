import typing as t

import click
from click.core import Context as Context
from click.core import Group as Group
from click.core import Option as Option
from click.core import Parameter as Parameter
from click.decorators import confirmation_option as confirmation_option
from click.decorators import help_option as help_option
from click.decorators import make_pass_decorator as make_pass_decorator
from click.decorators import pass_context as pass_context
from click.decorators import pass_obj as pass_obj
from click.decorators import password_option as password_option
from click.decorators import version_option as version_option
from click.exceptions import Abort as Abort
from click.exceptions import BadArgumentUsage as BadArgumentUsage
from click.exceptions import BadOptionUsage as BadOptionUsage
from click.exceptions import BadParameter as BadParameter
from click.exceptions import ClickException as ClickException
from click.exceptions import Exit as Exit
from click.exceptions import FileError as FileError
from click.exceptions import MissingParameter as MissingParameter
from click.exceptions import NoSuchOption as NoSuchOption
from click.exceptions import UsageError as UsageError
from click.types import BOOL as BOOL
from click.types import FLOAT as FLOAT
from click.types import INT as INT
from click.types import STRING as STRING
from click.types import UNPROCESSED as UNPROCESSED
from click.types import UUID as UUID
from click.types import Choice as Choice
from click.types import DateTime as DateTime
from click.types import File as File
from click.types import FloatRange as FloatRange
from click.types import IntRange as IntRange
from click.types import ParamType as ParamType
from click.types import Path as Path
from click.types import Tuple as Tuple
from click.utils import echo as echo
from click.utils import format_filename as format_filename
from click.utils import get_app_dir as get_app_dir
from click.utils import get_binary_stream as get_binary_stream
from click.utils import get_text_stream as get_text_stream
from click.utils import open_file as open_file
from ellar.threading import run_as_async

from .argument import Argument
from .command import Command
from .group import AppContextGroup, EllarCommandGroup
from .util import with_app_context


def argument(
    *param_decls: str,
    cls: t.Optional[t.Type[click.Argument]] = None,
    required: bool = True,
    help: t.Optional[str] = None,
    hidden: t.Optional[bool] = None,
    **attrs: t.Any,
) -> t.Callable:
    return click.argument(
        *param_decls,
        cls=cls or Argument,
        required=required,
        hidden=hidden,
        help=help,
        **attrs,
    )


def option(
    *param_decls: str, cls: t.Optional[t.Type[Option]] = None, **attrs: t.Any
) -> t.Callable:
    return click.option(*param_decls, cls=cls, **attrs)


def command(
    name: t.Optional[str] = None, cls: t.Optional[click.Command] = None, **attrs: t.Any
) -> t.Union[click.Command, t.Any]:
    return click.command(name=name, cls=cls or Command, **attrs)  # type:ignore[arg-type]


def group(
    name: t.Union[str, t.Callable, None] = None,
    cls: t.Optional[t.Type[click.Group]] = None,
    **attrs: t.Any,
) -> t.Callable:
    return click.group(name=name, cls=cls or AppContextGroup, **attrs)  # type:ignore[arg-type]


__all__ = [
    "argument",
    "run_as_async",
    "command",
    "Argument",
    "Option",
    "option",
    "AppContextGroup",
    "EllarCommandGroup",
    "with_app_context",
    "Context",
    "Group",
    "Parameter",
    "make_pass_decorator",
    "confirmation_option",
    "help_option",
    "group",
    "pass_context",
    "password_option",
    "version_option",
    "Abort",
    "BadArgumentUsage",
    "BadOptionUsage",
    "BadParameter",
    "ClickException",
    "FileError",
    "MissingParameter",
    "NoSuchOption",
    "UsageError",
    "pass_obj",
    "BOOL",
    "Choice",
    "DateTime",
    "File",
    "FLOAT",
    "FloatRange",
    "INT",
    "IntRange",
    "ParamType",
    "Path",
    "STRING",
    "Tuple",
    "UNPROCESSED",
    "UUID",
    "echo",
    "format_filename",
    "get_app_dir",
    "get_binary_stream",
    "get_text_stream",
    "open_file",
    "Exit",
]


def __dir__() -> t.List[str]:
    return sorted(__all__)  # pragma: no cover
