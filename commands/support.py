import click
from controller.EventController import EventController


def register_support_commands(cli):
    @cli.command()
    @click.pass_context
    def list_my_events(ctx):
        controller = EventController(ctx)
        controller.display_support_events()

    @cli.command()
    @click.pass_context
    def update_my_event(ctx):
        controller = EventController(ctx)
        controller.update_support_events()
