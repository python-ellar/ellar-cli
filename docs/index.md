<p align="center">
  <a href="#" target="blank"><img src="img/EllarLogoIconOnly.png" width="200" alt="Ellar Logo" /></a>
</p>

<p align="center"> Ellar CLI Tool for Scaffolding Ellar Projects and Modules and also running Ellar Commands</p>

![Test](https://github.com/eadwinCode/ellar-cli/actions/workflows/test_full.yml/badge.svg)
![Coverage](https://img.shields.io/codecov/c/github/eadwinCode/ellar-cli)
[![PyPI version](https://badge.fury.io/py/ellar-cli.svg)](https://badge.fury.io/py/ellar-cli)
[![PyPI version](https://img.shields.io/pypi/v/ellar-cli.svg)](https://pypi.python.org/pypi/ellar-cli)
[![PyPI version](https://img.shields.io/pypi/pyversions/ellar-cli.svg)](https://pypi.python.org/pypi/ellar-cli)

# Introduction
Ellar CLI is an abstracted tool for the Ellar web framework that helps in the standard project scaffold of the framework, module project scaffold, running the project local server using UVICORN, and running custom commands registered in the application module or any Ellar module.

## Requirements
- Python >= 3.7
- Ellar

## Installation
if you have [ellar](https://github.com/eadwinCode/ellar) install ready
```
pip install ellar-cli
```
Full installation

```shell
pip install ellar-cli[full]
```

### NB:
Some shells may treat square braces (`[` and `]`) as special characters. If that's the case here, then use a quote around the characters to prevent unexpected shell expansion.
```shell
pip install "ellar-cli[full]"
```

## Usage

```shell
ellar --help
```
