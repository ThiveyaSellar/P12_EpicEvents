import jwt, os
from argon2 import PasswordHasher

from models import User, Team
from views.RegisterView import RegisterView
from utils.validators import validate_password

from utils.TokenManagement import TokenManagement


class RegisterController:

    def __init__(self, ctx):
        self.view = RegisterView()
        self.session =ctx.obj["session"]
        self.SECRET_KEY = ctx.obj["SECRET_KEY"]

    def __hash_passwords(self, password):
        ph = PasswordHasher()
        return ph.hash(password)

    def write_in_netrc(self, access_token, refresh_token):
        netrc_path = TokenManagement.get_netrc_path()
        machine = "127.0.0.1"
        if not os.path.exists(netrc_path):
            TokenManagement.create_netrc_file(machine, access_token, refresh_token,
                              netrc_path)
        else:
            TokenManagement.update_tokens_in_netrc(machine, access_token, refresh_token,
                                   netrc_path)


    def email_exists_in_db(self, email):
        user = self.session.query(User).filter_by(email_address=email).first()
        return user is not None

    def register(self, email, password, password2, first_name, last_name, phone, team):

        if self.email_exists_in_db(email):
            self.view.message_email_exists()
            return

        if not validate_password(password, password2):
            self.view.print_password_error()
            return

        # Hachage du mot de passe
        hashed_password = self.__hash_passwords(password)

        # Récupérer l'id de l'équipe
        team_id = self.session.query(Team).filter_by(name=team).first().id

        # Création de l'utilisateur
        new_user = User(
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            email_address=email.strip().lower(),
            phone=phone,
            team_id=team_id
        )

        # Enregistrement dans la base de données
        self.session.add(new_user)
        self.session.commit()

        self.view.success_message(first_name, last_name)
