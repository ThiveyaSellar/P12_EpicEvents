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

Session = sessionmaker(bind=engine)
session = Session()

@click.group()
def cli():
    pass

# affichage
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

    # logique
    if password != password2:
        # affichage
        click.echo(f"Les mots de passe ne matchent pas.")
        return

    # logique
    ph = PasswordHasher()
    # Hachage du mot de passe
    hashed_password = ph.hash(password)

    # logique
    # Récupérer l'id de l'équipe
    team_id = session.query(Team).filter_by(name=team).one().id

    # Logique
    # Création de l'utilisateur
    new_user = User(
        password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        email_address=email,
        phone=phone,
        team_id=team_id
    )

    # Logique
    # Enregistrement dans la base de données
    session.add(new_user)
    session.commit()

    # affichage
    click.echo(f"Inscription réussie pour {first_name} {last_name}.")


class RegisterView:

    @cli.command()
    @click.option("--email", prompt="Email", help="Votre email")
    @click.option("--password", prompt="Mot de passe", hide_input=True,
                  help="Votre mot de passe")
    @click.option("--password2", prompt="Confirmation de mot de passe",
                  hide_input=True,
                  help="Votre mot de passe")
    @click.option("--first_name", prompt="Prénom", help="Votre prénom")
    @click.option("--last_name", prompt="Nom", help="Votre nom")
    @click.option("--phone", prompt="Numéro de téléphone",
                  help="Votre téléphone")
    @click.option("--team",
                  type=click.Choice(["Commercial", "Gestion", "Support"],
                                    case_sensitive=False),
                  prompt="Équipe", help="Votre équipe")
    def register(email, password, password2, first_name, last_name, phone,
                 team):
        return RegisterForm(email, password, password2, first_name, last_name,
                            phone, team)

    @staticmethod
    def msg_passwords_doesnt_match():
        click.echo(f"Les mots de passe ne matchent pas.")

    @staticmethod
    def msg_register_successful(first_name, last_name):
        click.echo(f"Inscription réussie pour {first_name} {last_name}.")


class RegisterForm:

    def __init__(self, email, password, password2, first_name, last_name, phone, team):
        self.email = email
        self.password = password
        self.password2 = password2
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.team = team
        self.hashed_password = self.__hash_passwords()

    def validate_passwords(self):
        return self.password == self.password2


class RegisterController:

    def register(self):

        registerView = RegisterView()
        registerForm = registerView.register()

        if registerForm.validate_passwords():
            team_id = session.query(Team).filter_by(
                name=registerForm.team
            ).one().id

            new_user = User(
                password=registerForm.hashed_password,
                first_name=registerForm.first_name,
                last_name=registerForm.last_name,
                email_address=registerForm.email,
                phone=registerForm.phone,
                team_id=team_id
            )

            # Enregistrement dans la base de données
            session.add(new_user)
            session.commit()

            RegisterView.msg_register_successful(registerForm.first_name, registerForm.last_name)
        else:
            # affichage
            RegisterView.msg_passwords_doesnt_match()


