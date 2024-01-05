import typing as t

from click.testing import CliRunner, Result

from .main import app_cli


class EllarCliRunner(CliRunner):
    def invoke_ellar_command(  # type: ignore
        self,
        args: t.Optional[t.Union[str, t.Sequence[str]]] = None,
        input: t.Optional[t.Union[bytes, t.Text, t.IO[t.Any]]] = None,
        env: t.Optional[t.Mapping[str, str]] = None,
        catch_exceptions: bool = True,
        color: bool = False,
        **extra: t.Any,
    ) -> Result:
        return super().invoke(
            app_cli,
            args=args,
            input=input,
            env=env,
            catch_exceptions=catch_exceptions,
            color=color,
            **extra,
        )
