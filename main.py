import os, sys, click, jwt, re

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

def email_exists_in_db(session, email):
    user = session.query(User).filter_by(email_address=email).first()
    return user is not None

def validate_email(ctx, param, value):
    email = value
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise click.BadParameter("L'email n'est pas valide.")
    # Vérifier dans le cas d'une inscription si le mail existe déjà ou non
    if ctx.command.name == "register":
        if email_exists_in_db(session, email):
            raise click.BadParameter("Cet email est déjà utilisé.")
    return email

def validate_phone(ctx, param, value):
    phone = value
    pattern = r"^0[1-9](\d{2}){4}$"
    if not re.match(pattern, phone):
        raise click.BadParameter("Le numéro n'est pas valide.")
    return phone

def validate_name(ctx, param, value):
    name = value
    if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\-']+$", name):
        if param.name == "last_name":
            label = "Nom"
        elif param.name == "first_name":
            label = "Prénom"
        else:
            label = param.name.capitalize()
        raise click.BadParameter(f"{label} invalide")
    return name

@click.group()
def cli():
    pass

@cli.command()
@click.option("--email", prompt="Email", callback=validate_email, help="Votre email")
@click.option("--password", prompt="Mot de passe", hide_input=True, help="Votre mot de passe")
def login(email, password):
    controller = LoginController()
    controller.login(email, password, session, SECRET_KEY)

@cli.command()
@click.option("--email", prompt="Email", callback=validate_email, help="Votre email")
@click.option("--password", prompt="Mot de passe", hide_input=True,
              help="Votre mot de passe")
@click.option("--password2", prompt="Confirmation de mot de passe",
              hide_input=True,
              help="Votre mot de passe")
@click.option("--first_name", prompt="Prénom", callback=validate_name, help="Votre prénom")
@click.option("--last_name", prompt="Nom", callback=validate_name, help="Votre nom")
@click.option("--phone", prompt="Numéro de téléphone", callback=validate_phone, help="Votre téléphone")
@click.option("--team", type=click.Choice(["Commercial", "Gestion", "Support"],
                                          case_sensitive=False),
              prompt="Équipe", help="Votre équipe")
def register(email, password, password2, first_name, last_name, phone, team):
    controller = RegisterController()
    controller.register(email, password, password2, first_name, last_name, phone, team, session, SECRET_KEY)

@cli.command()
def logout():
    controller = LoginController()
    controller.logout()

@cli.command()
def show_clients():
    controller = ClientController(session, SECRET_KEY)
    controller.display_all_clients(session)

@cli.command()
def show_events():
    controller = EventController(session, SECRET_KEY)
    controller.display_all_events(session)

@cli.command()
def show_contracts():
    controller = ContractController(session, SECRET_KEY)
    controller.display_all_contracts(session)

# --------------------------------------------------------
    # Support
# --------------------------------------------------------

@cli.command()
def show_support_events():
    controller = EventController(session, SECRET_KEY)
    controller.display_support_events()

@cli.command()
def update_support_event():
    controller = EventController(session, SECRET_KEY)
    controller.update_support_events()

# --------------------------------------------------------
    # Commercial
# --------------------------------------------------------

@cli.command()
def create_client():
    controller = ClientController(session, SECRET_KEY)
    controller.create_client()

@cli.command()
def update_client():
    controller = ClientController(session, SECRET_KEY)
    controller.update_client()

@cli.command()
def exit():
    controller = LoginController()
    controller.exit_program()
    sys.exit()

"""def main():

    print("A")
    menu_controller = MenuController()
    print("B")
    # Vérifier qu'il y a un token permettant d'identifier l'utilisateur et s'il est valide
    connected, user = TokenManagement.checking_user_connection(session, SECRET_KEY)
    print("C")

    if not connected:
        print("D")
        menu_controller.create_login_menu(cli)
        print("E")
        # menu_controller.create_login_menu(cli)
        user = TokenManagement.get_connected_user(session, SECRET_KEY)
        print("F")

    if user is None:
        print("USer is None")
        menu_controller.create_login_menu(cli)
    menu_controller.create_main_menu(user, cli)
    print("G")"""

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

    menu_controller.create_main_menu(user, cli)

if __name__ == "__main__":
    main()
