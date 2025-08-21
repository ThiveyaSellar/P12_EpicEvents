import textwrap
from sentry_sdk import logger as sentry_logger

import click

class MenuView:

    @staticmethod
    def ask_cmd_input():
        return input("Command > ").strip().lower()

    @staticmethod
    def message_already_connected():
        click.echo("You are already logged. Please log out before using this command.")

    @staticmethod
    def message_input_command():
        click.echo("Enter a command.")

    @staticmethod
    def message_invalid_cmd():
        click.echo("Invalid command, please try again.")

    @staticmethod
    def message_inexistant_cmd():
        click.echo("Inexistant command, please try again.")

    @staticmethod
    def message_unauthorized_cmd(team):
        click.echo(f"Command is unauthorized for the {team} team.")

    @staticmethod
    def msg_user_none():
        click.echo("Unknown user, exiting!")

    @staticmethod
    def print_connection_error():
        click.echo("Please login again.")

    @staticmethod
    def print_error_message(message):
        click.echo(message)

    @staticmethod
    def logout_message():
        click.echo("Logging out. Returning to the login menu...")


    @staticmethod
    def print_login_menu():
        menu = (
        "------------- Main -------------\n"
        "Please enter a command:\n"
        "register\n"
        "login\n"
        "exit"
        )
        click.secho(menu, fg="yellow", bold=True)

    @staticmethod
    def show_login_menu():

        options = {"register", "login", "exit"}
        while True:
            MenuView.print_login_menu()
            cmd = MenuView.ask_cmd_input()
            if cmd in options:
                return cmd
            MenuView.message_invalid_cmd()

    @staticmethod
    def show_sales_menu():
        menu = textwrap.dedent("""
            ------------- Sales menu -------------
            # Client
            list-clients
            create-my-client
            update-my-client
            # Contract
            list-contracts
            update-contract
            list-unpaid-contracts
            list-unsigned-contracts
            # Event
            list-events
            create-event-for-my-client
            logout
        """)
        click.secho(menu, fg="yellow", bold=True)

    @staticmethod
    def show_support_menu():
        menu = textwrap.dedent("""
            ------------- Support menu -------------
            # Event
            list-events
            list-my-events
            update-my-event
            # Client
            list-clients
            # Contract
            list-contracts
            logout
        """)
        click.secho(menu, fg="yellow", bold=True)

    @staticmethod
    def show_management_menu():
        menu = textwrap.dedent("""
            ------------- Management menu -------------
            # Co-worker
            list-co-workers
            create-co-worker
            update-co-worker
            delete-co-worker
            # Contract
            list-contracts
            create-contract
            update-contract
            # Client
            list-clients
            add-sales-rep-collab-to-client
            # Event
            list-events
            list-events-without-support
            list-events-without-contract
            add-support-collab-to-event
            logout
        """)
        click.secho(menu, fg="yellow", bold=True)

    @staticmethod
    def show_main_menu(user, team):
        click.echo(f"------------- Menu {team} -------------")
        click.echo("list-clients")
        click.echo("list-events")
        click.echo("logout")
