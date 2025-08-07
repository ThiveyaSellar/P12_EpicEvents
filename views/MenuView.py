import click

class MenuView:

    @staticmethod
    def ask_cmd_input():
        return input("Commande > ").strip().lower()

    @staticmethod
    def error_message_invalid_cmd():
        click.echo("Commande invalide, veuillez réessayer.")

    @staticmethod
    def msg_user_none():
        click.echo("Utilisateur inconnu, fin du programme!")

    @staticmethod
    def print_login_menu():
        click.echo("\n------------- Main -------------")
        click.echo("Please enter a command :")
        click.echo("1- register")
        click.echo("2- login")
        click.echo("3- exit")

    @staticmethod
    def show_login_menu():

        options = {"register", "login", "exit"}
        while True:
            MenuView.print_login_menu()
            cmd = MenuView.ask_cmd_input()
            if cmd in options:
                return cmd
            MenuView.error_message_invalid_cmd()

    @staticmethod
    def show_sales_menu():
        click.echo(f"------------- Sales menu -------------")
        # Client
        click.echo("list-clients")
        click.echo("create-my-client")
        click.echo("update-my-client")
        # Contract
        click.echo("list-contracts")
        click.echo("update-contract")
        click.echo("list-unpaid-contracts")
        click.echo("list-unsigned-contracts")
        # Event
        click.echo("list-events")
        click.echo("create-event-for-my-client")

        click.echo("logout")

    @staticmethod
    def show_support_menu():
        click.echo(f"------------- Support menu -------------")
        # Event
        click.echo("list-events")
        click.echo("list-my-events")
        click.echo("update-my-event")
        # Client
        click.echo("list-clients")
        # Contract
        click.echo("list-contracts")
        click.echo("logout")

    @staticmethod
    def show_management_menu():
        click.echo(f"------------- Management menu -------------")
        # Co-worker
        click.echo("list-co-workers")
        click.echo("create-co-worker")
        click.echo("update-co-worker")
        click.echo("delete-co-worker")
        # Contract
        click.echo("list-contracts")
        click.echo("create-contract")
        click.echo("update-contract")
        # Client
        click.echo("list-clients")
        # Event
        click.echo("list-events")
        click.echo("list-events-without-support")
        click.echo("list-events-without-contract")
        click.echo("add-support-collab-to-event")
        click.echo("logout")

    @staticmethod
    def show_main_menu(user, team):
        click.echo(f"------------- Menu {team} -------------")
        click.echo("list-clients")
        click.echo("list-events")
        click.echo("logout")

    @staticmethod
    def print_error_message(message):
        click.echo(message)

    @staticmethod
    def logout_message():
        click.echo("Déconnexion. Retour au menu de connexion...")