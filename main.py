import os, sys, click, jwt

# Ajouter le répertoire racine au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from utils.TokenManagement import TokenManagement
from models import User, Team, Event, Contract, Client

from controller.MenuController import MenuController
from controller.LoginController import LoginController
from controller.RegisterController import RegisterController
from controller.ClientController import ClientController
from controller.EventController import EventController
from controller.ContractController import ContractController

from settings import Settings

settings = Settings()
session = settings.session
SECRET_KEY = settings.secret_key

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
    controller = ClientController()
    controller.display_all_clients(session)

@cli.command()
def show_events():
    controller = EventController()
    controller.display_all_events(session)

@cli.command()
def show_support_events():
    controller = EventController()
    controller.display_support_events(session, SECRET_KEY)

@cli.command()
def show_contracts():
    controller = ContractController()
    controller.display_all_contracts(session)

def main():

    menu_controller = MenuController()
    connected, user = TokenManagement.checking_user_connection(session, SECRET_KEY)

    if not connected:
        menu_controller.create_login_menu(cli)
    menu_controller.create_main_menu(user, cli)

if __name__ == "__main__":
    main()
