import os, sys
# Ajouter le répertoire racine au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import configparser, click, jwt, datetime
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
from utils.db_utils import create_database_if_not_existent

# Récupérer les infos de connexion à la base de données depuis le fichier config.ini
config = configparser.ConfigParser()
config.read('config.ini')

db_user = config['database']['user']
db_password = config['database']['password']
db_host = config['database']['host']
db_name = config['database']['dbname']

# create_database_if_not_existent(db_user, db_password, db_host, db_name)

# Créer objet de connexion à la base de données
engine = create_engine(
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",
    echo=False
) # Ajouter echo=True pour afficher les logs des commandes SQL, retirer en production
conn = engine.connect()

# Afficher les tables de la base de données
"""result = conn.execute(text("SHOW TABLES;"))
for row in result:
    print(row)"""

Session = sessionmaker(bind=engine)
session = Session()

# Permet de mapper les classes avec les tables
Base = declarative_base()
# Créer les tables
Base.metadata.create_all(engine)

# Clé secrète pour signer le jeton JWT
SECRET_KEY = "nvlzhvgi476hcich90796"

@click.group()
def cli():
    pass

@cli.command()
@click.argument("nom")
def salut(nom):
    """Dit bonjour à l'utilisateur."""
    click.echo(f"Bonjour, {nom} !")

@cli.command()
@click.argument("nom")
def bye(nom):
    """Dit bonjour à l'utilisateur."""
    click.echo(f"Bye, {nom} !")

@cli.command()
@click.option("--email", prompt="Email", help="Votre email")
@click.option("--password", prompt="Mot de passe", hide_input=True,
              help="Votre mot de passe")
def login(email, password):
    """Commande de connexion"""
    try:
        # Vérification si le mail de l'utilisateur existe
        user = session.query(User).filter_by(email_address=email).one()

        # Permet d'hacher le mdp en version sécurisée et illisible
        # Permet de comparer avec un mdp haché stocké en base de données
        ph = PasswordHasher()
        try:
            ph.verify(user.password, password)
        except:
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
            print("Netrc updated")

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

def show_login_menu():
    options = {"register","login",}
    while True:
        click.echo("\n------------- Main -------------")
        click.echo("Please enter a command :")
        click.echo("1- register")
        click.echo("2- login")
        click.echo("3- exit")
    click.echo("------------- Main -------------")
    click.echo("Please enter a command :")
    click.echo("1- register")
    click.echo("2- login")
    click.echo("3- exit")
    cmd = input("Commande > ")
    while cmd.lower() not in ['login', 'register', 'exit']:
        click.echo("------------- Main -------------")
        click.echo("1- register")
        click.echo("2- login")
        click.echo("3- exit")
        cmd = input("Commande > ")
    return cmd

def main():
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
        cmd = show_login_menu()
        if cmd == 'exit':
            exit()
        cli.main(cmd.split(), standalone_mode=False)

    while True:
        try:
            click.echo(f"------------- Menu {user.team.name} -------------")
            print("Menu")
            click.echo("1- Inscription")
            click.echo("2- Connexion")
            click.echo("3- Quitter")
            cmd = input("Commande > ")
            if cmd.lower() in ["exit", "quit"]:
                break
            cli.main(cmd.split(), standalone_mode=False)
        except Exception as e:
            click.echo(f"Erreur : {e}")

if __name__ == "__main__":
    main()

