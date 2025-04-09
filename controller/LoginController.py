import click, jwt, os
from models import User, Team, Event, Contract, Client
from argon2 import PasswordHasher
from datetime import datetime, timedelta
from sqlalchemy.exc import NoResultFound

from utils.token_utils import  create_netrc_file, get_netrc_path, \
    get_tokens_from_netrc, update_tokens_in_netrc, get_user_from_access_token, \
    generate_tokens, is_token_expired

class LoginView:

    """@cli.command()
    @click.option("--email", prompt="Email", help="Votre email")
    @click.option("--password", prompt="Mot de passe", hide_input=True,
                  help="Votre mot de passe")
    def login(email, password):
        return LoginForm(email, password)"""

    @staticmethod
    def print_password_error():
        click.echo("Mot de passe incorrect.")

    @staticmethod
    def print_welcome_message(user):
        click.echo(f"Connexion réussie.")
        click.echo(f"Bienvenue {user.first_name} {user.last_name}!")

    @staticmethod
    def print_user_not_found():
        click.echo("Utilisateur introuvable.")

class LoginForm:

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def check_email_format(self):
        pass
        # ?

class LoginController:

    def login(self, email, password, session, SECRET_KEY):
        loginView = LoginView()

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
                LoginView.show_password_error()
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

            # Stocker le jeton dans le fichier .netrc
            # Définir le chemin du fichier .netrc dans le dossier utilisateur Windows

            # Enregistrer le refresh token dans la base de données
            user.token = refresh_token
            session.commit()

            # Données à écrire dans .netrc
            netrc_path = get_netrc_path()
            machine = "127.0.0.1"
            if not os.path.exists(netrc_path):
                create_netrc_file(machine, access_token, refresh_token,
                                  netrc_path)
            else:
                update_tokens_in_netrc(machine, access_token, refresh_token,
                                       netrc_path)

            loginView.print_welcome_message(user)

        except NoResultFound:
            LoginView.print_user_not_found()