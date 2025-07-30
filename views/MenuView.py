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
    def show_support_menu():
        click.echo(f"------------- Support menu -------------")
        click.echo("1- show-support-events")
        click.echo("2- update-support-event")
        click.echo("3- show-clients")
        click.echo("4- show-contracts")
        click.echo("5- show-events")
        click.echo("6- logout")

    @staticmethod
    def show_sales_menu():
        click.echo(f"------------- Sales menu -------------")
        click.echo("1- create-client")
        click.echo("2- update-client")
        click.echo("3- show-specific-contracts")
        click.echo("4- update-my-contracts")
        click.echo("5- create-event-for-my-client")
        click.echo("6- show-clients")
        click.echo("7- show-contracts")
        click.echo("8- show-events")
        click.echo("9- logout")

    @staticmethod
    def show_main_menu(user, team):
        click.echo(f"------------- Menu {team} -------------")
        click.echo("1- show-clients")
        click.echo("2- show-events")
        click.echo("3- logout")

    @staticmethod
    def print_error_message(message):
        click.echo(message)

    @staticmethod
    def logout_message():
        click.echo("Déconnexion. Retour au menu de connexion...")