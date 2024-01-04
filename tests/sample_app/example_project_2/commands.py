import ellar_cli.click as click


@click.group()
def db():
    pass


@db.command()
def create_migration():
    """Creates Database Migration"""
    print("create migration command from example_project_2")


@click.command()
def whatever_you_want():
    """Whatever you want"""
    print("Whatever you want command from example_project_2")


@click.command()
def project_2_command():
    """Project 2 Custom Command"""
    print("Project 2 Custom Command from example_project_2")
