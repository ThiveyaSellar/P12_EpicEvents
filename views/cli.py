import datetime

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

@cli.command()
@click.option("--email", prompt="Email", help="Votre email")
@click.option("--password", prompt="Mot de passe", hide_input=True, help="Votre mot de passe")
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
            "exp": datetime.now() + datetime.timedelta(minutes=3)  # Expiration dans 1h
        }
        access_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        payload = {
            "user_id": user.id,
            "email": user.email_address,
            "role": user.team.name,
            "exp": datetime.now() + datetime.timedelta(minutes=5)
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
            update_tokens_in_netrc(machine, access_token, refresh_token, netrc_path)

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
@click.option("--password2", prompt="Confirmation de mot de passe", hide_input=True,
              help="Votre mot de passe")
@click.option("--first_name", prompt="Prénom", help="Votre prénom")
@click.option("--last_name", prompt="Nom", help="Votre nom")
@click.option("--phone", prompt="Numéro de téléphone", help="Votre téléphone")
@click.option("--team", type=click.Choice(["Commercial","Gestion","Support"], case_sensitive=False), prompt="Équipe", help="Votre équipe")
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