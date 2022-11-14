This is a quick example of how to create a custom command. Also, hints on working of ella cli.

Ellar CLI tools is a wrapper round [typer](), 
so it's easy to get CLI context available in the command action.
Ellar CLI exposes some cli context necessary for validation and interacting with ellar project.

Create a file `commands.py` in root project
```python
import typing as t
import typer
from ellar.common import command
from ellar_cli.service import EllarCLIService
from ellar_cli.constants import ELLAR_META

@command
def my_new_command(ctx:typer.Context):
    """my_new_command cli description """
    ellar_cli_service = t.cast(t.Optional[EllarCLIService], ctx.meta.get(ELLAR_META))
```
`ellar_cli_service` holds ellar project meta-data
Lets, make the `my_new_command` visible on the cli.

In `ApplicationModule`, add the command to `Module` commands parameter 
```python
from ellar.common import Module
from ellar.core import ModuleBase
from .commands import my_new_command

@Module(commands=[my_new_command])
class ApplicationModule(ModuleBase):
    pass
```
open your terminal and navigate to project directory and run the command below
```shell
ellar db --help
```
command output
```shell
Usage: Ellar, Python Web framework [OPTIONS] COMMAND [ARGS]...

Options:
  -p, --project TEXT              Run Specific Command on a specific project
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  create-module   - Scaffolds Ellar Application Module -
  create-project  - Scaffolds Ellar Application -
  my-new-command  my_new_command cli description
  new             - Runs a complete Ellar project scaffold and creates...
  runserver       - Starts Uvicorn Server -
  say-hi 
```
