import os, sys, click, jwt

# Ajouter le répertoire racine au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from utils.token_utils import checking_user_connection
from models import User, Team, Event, Contract, Client

from controller.MenuController import MenuController
from controller.LoginController import LoginController
from controller.RegisterController import RegisterController

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
    connected, user = checking_user_connection(session, SECRET_KEY)

    if not connected:
        menu_controller.create_login_menu(cli)
    menu_controller.create_main_menu(user, cli)

if __name__ == "__main__":
    main()
