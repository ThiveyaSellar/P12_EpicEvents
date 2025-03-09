import configparser, click, jwt, os, sys

from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ajouter le répertoire racine au sys.path
from views.cli import display_login_registration_menu
from models.models import User, Team
from utils.token_utils import get_netrc_path, get_tokens_from_netrc, \
    update_tokens_in_netrc, get_user_from_access_token
from utils.token_utils import generate_tokens, is_token_expired
from utils.db_utils import create_database_if_not_existent
from views.cli import cli  # Importer la fonction cli


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

"""
    # -----------------------------------------------------------------------
"""

import datetime
from datetime import datetime, timedelta


import click, jwt, os

from sqlalchemy.exc import NoResultFound

from argon2 import PasswordHasher

from models.models import Team, User
from utils.token_utils import create_netrc_file, update_tokens_in_netrc, \
    get_netrc_path

@click.group()
def cli():
    """Interface en ligne de commande"""
    pass


@cli.command()
def seed_teams():
    """Ajoute des équipes par défaut à la base de données."""
    default_teams = ["Commercial", "Gestion", "Support"]

    for team_name in default_teams:
        if not session.query(Team).filter_by(name=team_name).first():
            team = Team(name=team_name)
            session.add(team)
            click.echo(f"Équipe '{team_name}' ajoutée.")
        else:
            click.echo(f"Équipe '{team_name}' existe déjà.")

    session.commit()
    click.echo("Toutes les équipes par défaut ont été ajoutées.")


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


def display_login_registration_menu(session, SECRET_KEY):
    click.echo("Bienvenue !")
    choice = click.prompt(
        "Choisissez une option : 1- Connexion 2- Inscription", type=int)
    while choice not in [1, 2]:
        click.echo("Choix invalide, veuillez réessayer.")
        choice = click.prompt(
            "Choisissez une option : 1- Connexion, 2- Inscription",
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

@cli.command()
def seed_teams():

    """Ajoute des équipes par défaut à la base de données."""
    default_teams = ["Commercial","Gestion","Support"]

    for team_name in default_teams:
        if not session.query(Team).filter_by(name=team_name).first():
            team = Team(name=team_name)
            session.add(team)
            click.echo(f"Équipe '{team_name}' ajoutée.")
        else:
            click.echo(f"Équipe '{team_name}' existe déjà.")

    session.commit()
    click.echo("Toutes les équipes par défaut ont été ajoutées.")

"""
    # -----------------------------------------------------------------------
"""


def check_permissions(user, team):
    if user.get("team") == team:
        return True
    return False



def main():

    expired_session = False
    netrc_path = get_netrc_path()
    machine = "127.0.0.1"
    # Récupérer les tokens dans le fichier .netrc
    access_token, refresh_token = get_tokens_from_netrc(machine, netrc_path)
    if not access_token and refresh_token:
        # Inscription ou première connexion
        display_login_registration_menu(session, SECRET_KEY)
    else:
        # Récupérer les informations de l'utilisateur deouis le jeton d'accès
        user = get_user_from_access_token(
            refresh_token,
            SECRET_KEY,
            session
        )

        if is_token_expired(access_token):
            if is_token_expired(refresh_token):
                expired_session = True
            else:
                # Générer un nouveau access token
                access_token, refresh_token = generate_tokens(user, SECRET_KEY)
                update_tokens_in_netrc(
                    machine, access_token, refresh_token, netrc_path
                )

        if expired_session:
            click.echo("Session expirée.")
            display_login_registration_menu(session, SECRET_KEY)
        else:
            click.echo(f"Bienvenue {user.first_name} !")
            if user.team.name == "Commercial":
                click.echo("Vous êtes dans l'équipe commerciale.")
            elif user.team.name == "Gestion":
                click.echo("Vous êtes dans l'équipe de gestion.")
            elif user.team.name == "Support":
                click.echo("Vous êtes dans l'équipe de support.")

if __name__ == "__main__":
    # cli()
    main()
