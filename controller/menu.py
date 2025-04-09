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
from views.MenuView import MenuView

from settings import Settings

settings = Settings()
session = settings.session
SECRET_KEY = settings.secret_key

class MenuController:

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
                self.view.show_main_menu(team)
                cmd = self.view.ask_cmd_input()
                if cmd.lower() in ["exit", "quit"]:
                    break
                cli.main(cmd.split(), standalone_mode=False)
            except Exception as e:
                click.echo(f"Erreur : {e}")
                break

class RegisterView:

    def print_password_error(self):
        click.echo(f"Les mots de passe ne matchent pas.")

    def success_message(self, first_name, last_name):
        click.echo(f"Inscription réussie pour {first_name} {last_name}.")


class RegisterController:

    def validate_password(self, password, password2):
        return password == password2

    def __hash_passwords(self, password):
        ph = PasswordHasher()
        return ph.hash(password)

    def register(self, email, password, password2, first_name, last_name, phone, team):
        registerView = RegisterView()

        if not self.validate_password(password, password2):
            registerView.print_password_error()
            return

        # Hachage du mot de passe
        hashed_password = self.__hash_passwords(password)

        # Récupérer l'id de l'équipe
        team_id = session.query(Team).filter_by(name=team).one().id

        # Création de l'utilisateur
        new_user = User(
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            email_address=email,
            phone=phone,
            team_id=team_id
        )

        # Enregistrement dans la base de données
        session.add(new_user)
        session.commit()

        registerView.success_message(first_name, last_name)

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


"""
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
    if password != password2:
        click.echo(f"Les mots de passe ne matchent pas.")
        return

    ph = PasswordHasher()
    # Hachage du mot de passe
    hashed_password = ph.hash(password)

    # Récupérer l'id de l'équipe
    team_id = session.query(Team).filter_by(name=team).one().id

    # Création de l'utilisateur
    new_user = User(
        password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        email_address=email,
        phone=phone,
        team_id=team_id
    )

    # Enregistrement dans la base de données
    session.add(new_user)
    session.commit()

    click.echo(f"Inscription réussie pour {first_name} {last_name}.")
"""

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
