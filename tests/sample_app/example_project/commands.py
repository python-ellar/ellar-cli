import click
from ellar.common import EllarTyper, command

db = EllarTyper(name="db")


@db.command()
def create_migration():
    """Creates Database Migration"""
    print("create migration command")


@command()
def whatever_you_want():
    """Whatever you want"""
    print("Whatever you want command")


@click.command()
def say_hello():
    click.echo("Hello from ellar.")
