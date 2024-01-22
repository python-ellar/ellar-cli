import os

from ellar.common.constants import ELLAR_CONFIG_MODULE

from ellar_cli.main import create_ellar_cli

os.environ.setdefault(ELLAR_CONFIG_MODULE, "plain_project.config:DevelopmentConfig")


if __name__ == "__main__":
    # initialize Commandline program
    cli = create_ellar_cli("plain_project.server:bootstrap")
    # start commandline execution
    cli(prog_name="Ellar Web Framework CLI")
