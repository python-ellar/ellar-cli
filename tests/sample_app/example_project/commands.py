from ellar.core import Config, current_injector

import ellar_cli.click as click


@click.group(name="db")
def db():
    pass


@db.command()
def create_migration():
    """Creates Database Migration"""
    print("create migration command")


@click.command()
def whatever_you_want():
    """Whatever you want"""
    print("Whatever you want command")


@click.command()
def say_hello():
    click.echo("Hello from ellar.")


@db.command(name="command-with-context")
@click.with_injector_context
def command_with_app_context():
    print(
        f"Running a command with application context - {current_injector.get(Config).APPLICATION_NAME}"
    )
