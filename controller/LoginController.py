import jwt, os
from models import User
from argon2 import PasswordHasher
from datetime import datetime, timedelta
from sqlalchemy.exc import NoResultFound

from utils.TokenManagement import TokenManagement
from utils.db_helpers import commit_to_db

from views.LoginView import LoginView

import logging

logger = logging.getLogger(__name__)

class LoginController:

    def __init__(self, ctx):
        self.view = LoginView()
        self.session = ctx.obj["session"]
        self.SECRET_KEY = ctx.obj["SECRET_KEY"]

    def __hash_passwords(self, password):
        ph = PasswordHasher()
        return ph.hash(password)


    def check_user_mail(self, email):
        # Récupération utilisateur associé au mail
        email = email.strip().lower()

        return self.session.query(User).filter_by(email_address=email).one()

    def define_token(self, user, SECRET_KEY, time):
        payload = {
            "user_id": user.id,
            "email": user.email_address,
            "role": user.team.name,
            "exp": datetime.now() + timedelta(minutes=time)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token

    def write_in_netrc(self, access_token, refresh_token):
        netrc_path = TokenManagement.get_netrc_path()
        machine = "127.0.0.1"
        if not os.path.exists(netrc_path):
            TokenManagement.create_netrc_file(machine, access_token, refresh_token,
                              netrc_path)
        else:
            TokenManagement.update_tokens_in_netrc(machine, access_token, refresh_token,
                                   netrc_path)

    def verify_password(self, ph, user_password, password):
        try:
            return ph.verify(user_password, password)
        except:
            return False

    def login(self, email, password):
        self.session.expire_all()
        ph = PasswordHasher()

        # Vérifier l'email utilisé pour la connexion
        # Récupérer l'utilisateur associé
        try:
            user = self.check_user_mail(email.strip().lower())
        except NoResultFound:
            self.view.print_user_not_found()
            return
        # Vérifier le mot de passe saisi
        # avec le mot de passe de l'utilisateur récupéré
        if not self.verify_password(ph, user.password, password):
            self.view.print_password_error()
            return

        # Générer les tokens
        access_token = self.define_token(user, self.SECRET_KEY, 1)
        refresh_token = self.define_token(user, self.SECRET_KEY, 3)

        # Sauvegarder le token de rafraichissement dans la base de données
        user.token = refresh_token
        commit_to_db(self.session, self.view)

        # Ecrire les tokens dans le fichier netrc
        self.write_in_netrc(access_token, refresh_token)
        self.view.print_welcome_message(user)

    def logout(self):
        # Demander confirmation de déconnexion
        logging_out = self.view.get_logout_confirmation()
        machine = "127.0.0.1"
        if logging_out:
            netrc_path = TokenManagement.get_netrc_path()
            TokenManagement.update_tokens_in_netrc(machine,"","",netrc_path)
            self.view.print_logged_out_message()
            exit()
        else:
            self.view.print_staying_logged_message()

    def exit_program(self):
        self.view.print_exit_message()

    def change_password(self):
        # Afficher le mail de l'utilisateur courant et récupérer l'ancien mot de passe
        connected, user = TokenManagement.checking_user_connection(
            self.session,
            self.SECRET_KEY)
        # Demander l'ancien mot de passe
        old_pwd = LoginView.ask_old_password(user.email_address)
        ph = PasswordHasher()
        while not self.verify_password(ph, user.password, old_pwd):
            old_pwd = LoginView.ask_old_pwd_again()
        # Demander le nouveau mot de passe
        new_pwd, new_pwd_2 = LoginView.get_new_passwords()
        while not new_pwd == new_pwd_2:
            new_pwd, new_pwd_2 = LoginView.ask_new_passwords_again()

        # Hachage du nouveau mot de passe
        hashed_password = self.__hash_passwords(new_pwd)

        user.password = hashed_password
        commit_to_db(self.session,self.view)
        netrc_path = TokenManagement.get_netrc_path()
        machine = "127.0.0.1"
        TokenManagement.update_tokens_in_netrc(machine, "", "", netrc_path)
        self.view.confirm_update_and_login()
        exit()