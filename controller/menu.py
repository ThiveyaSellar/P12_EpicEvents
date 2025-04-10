import os, sys, click, jwt, datetime
from argon2 import PasswordHasher
from datetime import datetime, timedelta
from sqlalchemy.exc import NoResultFound

# Ajouter le répertoire racine au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from utils.token_utils import  create_netrc_file, get_netrc_path, \
    get_tokens_from_netrc, update_tokens_in_netrc, get_user_from_access_token, \
    generate_tokens, is_token_expired
from models import User, Team, Event, Contract, Client

# from MenuController import MenuController
from LoginController import LoginController
from RegisterController import RegisterController
from views.MenuView import MenuView

from settings import Settings

settings = Settings()
session = settings.session
SECRET_KEY = settings.secret_key

"""class MenuController:

    def __init__(self):
        self.view = MenuView()

    def create_login_menu(self):
        cmd = self.view.show_login_menu()
        if cmd == 'exit':
            exit()
        cli.main(cmd.split(), standalone_mode=False)

    def create_main_menu(self, user):
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
                click.echo(f"Erreur : {e}")
                break"""


@click.group()
def cli():
    pass


@cli.command()
@click.option("--email", prompt="Email", help="Votre email")
@click.option("--password", prompt="Mot de passe", hide_input=True, help="Votre mot de passe")
def login(email, password):
    controller = LoginController()
    controller.login(email, password, session, SECRET_KEY)

@cli.command()
@click.option("--email", prompt="Email", help="Votre email")
@click.option("--password", prompt="Mot de passe", hide_input=True,
              help="Votre mot de passe")
@click.option("--password2", prompt="Confirmation de mot de passe",
              hide_input=True,
              help="Votre mot de passe")
@click.option("--first_name", prompt="Prénom", help="Votre prénom")
@click.option("--last_name", prompt="Nom", help="Votre nom")
@click.option("--phone", prompt="Numéro de téléphone", help="Votre téléphone")
@click.option("--team", type=click.Choice(["Commercial", "Gestion", "Support"],
                                          case_sensitive=False),
              prompt="Équipe", help="Votre équipe")
def register(email, password, password2, first_name, last_name, phone, team):
    controller = RegisterController()
    controller.register(email, password, password2, first_name, last_name, phone, team)

@cli.command()
def show_clients():
    clients = session.query(Client).all()
    click.echo("------------- Clients -------------")
    for client in clients:
        click.echo(f"{client.first_name} {client.last_name}")

@cli.command()
def show_events():
    events = session.query(Event).all()
    click.echo("------------- Events -------------")
    for event in events:
        click.echo(f"{event.name} {event.end_date}")


def main():

    menu_controller = MenuController()
    machine = "127.0.0.1"
    netrc_path = get_netrc_path()
    connected = False
    access_token, refresh_token = get_tokens_from_netrc(machine, netrc_path)

    if access_token and refresh_token:
        # Récupérer les informations de l'utilisateur dans le jeton d'accès
        user = get_user_from_access_token(access_token, SECRET_KEY, session)
        if is_token_expired(access_token):
            if is_token_expired(refresh_token):
                connected = False
            else:
                # Générer un nouveau access token
                access_token, refresh_token = generate_tokens(user, SECRET_KEY)
                update_tokens_in_netrc(
                    machine, access_token, refresh_token, netrc_path
                )
                connected = True
    if not connected:
        menu_controller.create_login_menu()

    menu_controller.create_main_menu(user)



if __name__ == "__main__":
    main()
