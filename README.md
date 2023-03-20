<p align="center">
  <a href="#" target="blank"><img src="docs/img/EllarLogoIconOnly.png" width="200" alt="Ellar Logo" /></a>
</p>

<p align="center"> Ellar CLI Tool for Scaffolding Ellar Projects and Modules and also running Ellar Commands</p>

![Test](https://github.com/eadwinCode/ellar-cli/actions/workflows/test_full.yml/badge.svg)
![Coverage](https://img.shields.io/codecov/c/github/eadwinCode/ellar-cli)
[![PyPI version](https://badge.fury.io/py/ellar-cli.svg)](https://badge.fury.io/py/ellar-cli)
[![PyPI version](https://img.shields.io/pypi/v/ellar-cli.svg)](https://pypi.python.org/pypi/ellar-cli)
[![PyPI version](https://img.shields.io/pypi/pyversions/ellar-cli.svg)](https://pypi.python.org/pypi/ellar-cli)

# Introduction
Ellar CLI is an abstracted tool for the Ellar web framework that helps in the standard project scaffold of the 
framework, module project scaffold, running the project local server using UVICORN, and running custom commands registered in the application module or any Ellar module.

## Installation
if you have [ellar](https://github.com/eadwinCode/ellar) install ready
```
pip install ellar-cli
```

## Usage
To verify ellar-cli is working, run the command belove
```shell
ellar --help
```
Above command should output this:
```
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
  new             - Runs a complete Ellar project scaffold and creates...
  runserver       - Starts Uvicorn Server -
  say-hi

```

Full Documentation: [Here](https://eadwincode.github.io/ellar/commands)
