from argon2 import PasswordHasher

from models import User, Team
from views.RegisterView import RegisterView

from settings import Settings

settings = Settings()
session = settings.session
SECRET_KEY = settings.secret_key


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