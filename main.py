import os, sys, click, jwt, re
# Ajouter le répertoire racine au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from utils.TokenManagement import TokenManagement
from models import User, Team, Event, Contract, Client
from utils.validators import validate_email_callback, validate_phone_callback, validate_name


from controller.UserController import UserController
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
@click.pass_context
def cli(ctx):
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj["session"] = session
    ctx.obj["SECRET_KEY"] = SECRET_KEY

@cli.command()
@click.pass_context
@click.option("--email", prompt="Email", callback=validate_email_callback, help="Votre email")
@click.option("--password", prompt="Mot de passe", hide_input=True, help="Votre mot de passe")
def login(ctx, email, password):
    controller = LoginController(ctx)
    controller.login(email, password)

@cli.command()
@click.pass_context
@click.option("--email", prompt="Email", callback=validate_email_callback, help="Votre email")
@click.option("--password", prompt="Mot de passe", hide_input=True,
              help="Votre mot de passe")
@click.option("--password2", prompt="Confirmation de mot de passe",
              hide_input=True,
              help="Votre mot de passe")
@click.option("--first_name", prompt="Prénom", callback=validate_name, help="Votre prénom")
@click.option("--last_name", prompt="Nom", callback=validate_name, help="Votre nom")
@click.option("--phone", prompt="Numéro de téléphone", callback=validate_phone_callback, help="Votre téléphone")
@click.option("--team", type=click.Choice(["Commercial", "Gestion", "Support"],
                                          case_sensitive=False),
              prompt="Équipe", help="Votre équipe")
def register(ctx, email, password, password2, first_name, last_name, phone, team):
    controller = RegisterController(ctx)
    controller.register(email, password, password2, first_name, last_name, phone, team)

@cli.command()
@click.pass_context
def logout(ctx):
    controller = LoginController(ctx)
    controller.logout()

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
    controller.display_all_contracts()

# --------------------------------------------------------
    # Support
# --------------------------------------------------------

@cli.command()
@click.pass_context
def list_my_events(ctx):
    controller = EventController(ctx)
    controller.display_support_events()

@cli.command()
@click.pass_context
def update_my_event(ctx):
    controller = EventController(ctx)
    controller.update_support_events()

# --------------------------------------------------------
    # Management
# --------------------------------------------------------

@cli.command()
@click.pass_context
@click.option("--email", prompt="Email", callback=validate_email_callback, help="Son email")
@click.option("--first_name", prompt="Prénom", callback=validate_name, help="Son prénom")
@click.option("--last_name", prompt="Nom", callback=validate_name, help="Son nom")
@click.option("--phone", prompt="Numéro de téléphone", callback=validate_phone_callback, help="Son téléphone")
@click.option("--team", type=click.Choice(["Commercial", "Gestion", "Support"],
                                          case_sensitive=False),
              prompt="Son équipe", help="Son équipe")
def create_co_worker(ctx, email,first_name, last_name, phone, team):
    controller = UserController(ctx)
    controller.create_co_worker(email,first_name, last_name, phone, team)

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

# --------------------------------------------------------
    # Commercial
# --------------------------------------------------------

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
def exit(ctx):
    controller = LoginController(ctx)
    controller.exit_program()
    sys.exit()

@cli.command()
@click.pass_context
def create_event_for_my_client(ctx):
    controller = EventController(ctx)
    controller.create_event_for_my_client()

# --------------------------------------------------------
    # Main
# --------------------------------------------------------
def main():
    menu_controller = MenuController()
    # Vérifier qu'il y a un token permettant d'identifier l'utilisateur et s'il est valide
    connected, user = TokenManagement.checking_user_connection(session,
                                                               SECRET_KEY)
    while not connected:
        # Menu avec soit inscription soit connexion
        # Execution des commandes login et register
        menu_controller.create_login_menu(cli)
        # Vérification de l'execution de login

        # Vérifier si l'utilisateur est connecté (s'il s'est loggé)
        connected, user = TokenManagement.checking_user_connection(session,
                                                                   SECRET_KEY)

    menu_controller.create_main_menu(user, cli, session, SECRET_KEY)

if __name__ == "__main__":
    main()
