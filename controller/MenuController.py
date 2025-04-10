import click
from views.MenuView import MenuView

from controller.LoginController import LoginView


class MenuView:

    @staticmethod
    def ask_cmd_input():
        return input("Commande > ").strip().lower()

    @staticmethod
    def error_message_invalid_cmd():
        click.echo("Commande invalide, veuillez réessayer.")

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
    def show_main_menu(user, team):
        click.echo(f"------------- Menu {team} -------------")
        click.echo("1- show-clients")
        click.echo("2- show-events")
        click.echo("4- logout")

    @staticmethod
    def print_error_message(e):
        click.echo(f"Erreur : {e}")


class MenuController:

    def __init__(self):
        self.view = MenuView()

    def create_login_menu(self, cli):
        cmd = self.view.show_login_menu()
        if cmd == 'exit':
            exit()
        cli.main(cmd.split(), standalone_mode=False)

    def create_main_menu(self, user, cli):
        while True:
            try:
                team = user.team.name
                # Print menu and get command from user input
                self.view.show_main_menu(user, team)
                cmd = self.view.ask_cmd_input()
                if cmd.lower() in ["exit", "quit"]:
                    break
                cli.main(cmd.split(), standalone_mode=False)
            except Exception as e:
                self.view.print_error_message(e)
                break