import click

from controller.ClientController import ClientController
from controller.ContractController import ContractController
from controller.EventController import EventController


def register_sales_rep_commands(cli):
    @cli.command()
    @click.pass_context
    def create_my_client(ctx):
        controller = ClientController(ctx)
        controller.create_client()

    @cli.command()
    @click.pass_context
    def update_my_client(ctx):
        controller = ClientController(ctx)
        controller.update_client()

    @cli.command()
    @click.pass_context
    def create_event_for_my_client(ctx):
        controller = EventController(ctx)
        controller.create_event_for_my_client()

    @cli.command()
    @click.pass_context
    def list_unpaid_contracts(ctx):
        controller = ContractController(ctx)
        controller.list_unpaid_contracts()

    @cli.command()
    @click.pass_context
    def list_unsigned_contracts(ctx):
        controller = ContractController(ctx)
        controller.list_unsigned_contracts()

    @cli.command()
    @click.pass_context
    def sign_contract(ctx):
        controller = ContractController(ctx)
        controller.sign_contract()
