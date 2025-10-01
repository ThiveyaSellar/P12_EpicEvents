import click

from controller.ClientController import ClientController
from controller.ContractController import ContractController
from controller.EventController import EventController
from controller.UserController import UserController
from utils.validators import validate_email_callback, validate_name, \
    validate_phone_callback


def register_management_commands(cli):
    @cli.command()
    @click.pass_context
    def list_co_workers(ctx):
        controller = UserController(ctx)
        controller.display_co_workers()

    @cli.command()
    @click.pass_context
    @click.option("--email", prompt="Email", callback=validate_email_callback,
                  help="Son email")
    @click.option("--first_name", prompt="Prénom", callback=validate_name,
                  help="Son prénom")
    @click.option("--last_name", prompt="Nom", callback=validate_name,
                  help="Son nom")
    @click.option("--phone", prompt="Numéro de téléphone",
                  callback=validate_phone_callback, help="Son téléphone")
    @click.option("--team",
                  type=click.Choice(["Sales", "Management", "Support"],
                                    case_sensitive=False),
                  prompt="Son équipe", help="Son équipe")
    def create_co_worker(ctx, email, first_name, last_name, phone, team):
        controller = UserController(ctx)
        controller.create_co_worker(email, first_name, last_name, phone, team)

    @cli.command()
    @click.pass_context
    def update_co_worker(ctx):
        controller = UserController(ctx)
        controller.update_co_worker()

    @cli.command()
    @click.pass_context
    def delete_co_worker(ctx):
        controller = UserController(ctx)
        controller.delete_co_worker()

    @cli.command()
    @click.pass_context
    def create_contract(ctx):
        controller = ContractController(ctx)
        controller.create_contract()

    @cli.command()
    @click.pass_context
    def update_contract(ctx):
        controller = ContractController(ctx)
        controller.update_contract()

    @cli.command()
    @click.pass_context
    def list_events_without_support(ctx):
        controller = EventController(ctx)
        controller.list_events_without_support()

    @cli.command()
    @click.pass_context
    def list_events_without_contract(ctx):
        controller = EventController(ctx)
        controller.list_events_without_contract()

    @cli.command()
    @click.pass_context
    def add_support_collab_to_event(ctx):
        controller = EventController(ctx)
        controller.add_support_collab_to_event()

    @cli.command()
    @click.pass_context
    def add_sales_rep_collab_to_client(ctx):
        controller = ClientController(ctx)
        controller.add_sales_rep_collab_to_client()
