import click

from controller.ClientController import ClientController
from controller.ContractController import ContractController
from controller.EventController import EventController


def register_common_commands(cli):
    @cli.command()
    @click.pass_context
    def list_clients(ctx):
        controller = ClientController(ctx)
        controller.get_all_clients()

    @cli.command()
    @click.pass_context
    def list_events(ctx):
        controller = EventController(ctx)
        controller.get_all_events()

    @cli.command()
    @click.pass_context
    def list_contracts(ctx):
        controller = ContractController(ctx)
        controller.list_contracts()