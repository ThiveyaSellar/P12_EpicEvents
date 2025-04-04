import os, sys
# Ajouter le répertoire racine au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import click, jwt, datetime
from datetime import datetime, timedelta
from argon2 import PasswordHasher

from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import NoResultFound


from models import User, Team, Event, Contract, Client
# from views.cli import display_login_registration_menu
from utils.token_utils import  create_netrc_file, get_netrc_path, get_tokens_from_netrc, \
    update_tokens_in_netrc, get_user_from_access_token
from utils.token_utils import generate_tokens, is_token_expired

import LoginController
# from MenuController import MenuController
from views.MenuView import MenuView

from settings import Settings

settings = Settings()

session = settings.session

SECRET_KEY = settings.secret_key


class MenuController:

    def __init__(self):
        self.view = MenuView()

    @staticmethod
    @click.group()
    def cli():
        pass

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

@click.group()
def cli():
    pass

@cli.command()
@click.option("--email", prompt="Email", help="Votre email")
@click.option("--password", prompt="Mot de passe", hide_input=True,
              help="Votre mot de passe")
def login(email, password):
    #Commande de connexion
    # logique
    try:
        # Vérification si le mail de l'utilisateur existe
        user = session.query(User).filter_by(email_address=email).one()

        # Permet d'hacher le mdp en version sécurisée et illisible
        # Permet de comparer avec un mdp haché stocké en base de données
        ph = PasswordHasher()
        try:
            ph.verify(user.password, password)
        except:
            # affichage
            click.echo("Mot de passe incorrect.")
            return

        # Génération des jetons d'accès et de rafraichissement JWT
        payload = {
            "user_id": user.id,
            "email": user.email_address,
            "role": user.team.name,
            "exp": datetime.now() + timedelta(hours=1)
            # Expiration dans 1h
        }
        access_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        payload = {
            "user_id": user.id,
            "email": user.email_address,
            "role": user.team.name,
            "exp": datetime.now() + timedelta(hours=3)
        }
        refresh_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        netrc_path = get_netrc_path()

        # Stocker le jeton dans le fichier .netrc
        # Définir le chemin du fichier .netrc dans le dossier utilisateur Windows

        # Données à écrire dans .netrc
        machine = "127.0.0.1"

        if not os.path.exists(netrc_path):
            create_netrc_file(machine, access_token, refresh_token, netrc_path)
        else:
            update_tokens_in_netrc(machine, access_token, refresh_token,
                                   netrc_path)
        # Enregistrer le refresh token dans la base de données
        user.token = refresh_token
        session.commit()

        click.echo(f"Connexion réussie.")
        click.echo(f"Bienvenue {user.first_name} {user.last_name}!")

    except NoResultFound:
        click.echo("Utilisateur introuvable.")


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

def display_menu(user):
    click.echo(f"Bienvenue {user.first_name} !")

def display_login_registration_menu(session, SECRET_KEY):
    click.echo("------------- Menu principal -------------")
    click.echo("1- Inscription")
    click.echo("2- Connexion")
    click.echo("3- Quitter")
    choice = click.prompt(
        "Choisissez une option : 1- Connexion 2- Inscription", type=int)
    while choice not in [1, 2, 3]:
        click.echo("Choix invalide, veuillez réessayer.")
        choice = click.prompt(
            "Choisissez une option : 1- Connexion, 2- Inscription, 3- Quitter",
            type=int
        )
    # On exécute la commande en fonction du choix de l'utilisateur
    if choice == 1:
        # Connexion
        click.echo("Vous avez choisi de vous connecter.")
        cli(["login"])
    elif choice == 2:
        # Inscription
        click.echo("Vous avez choisi de vous inscrire.")
        cli(["register"])
    elif choice == 3:
        # Quitter
        click.echo("Vous avez choisi de quitter.")
        return

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
