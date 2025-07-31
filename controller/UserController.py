import random
import string
from argon2 import PasswordHasher

from models import User, Team
from utils.TokenManagement import TokenManagement
from views.UserView import UserView

class UserController:

    def __init__(self,session, SECRET_KEY):
        self.view = UserView()
        self.session = session
        self.SECRET_KEY = SECRET_KEY

    @staticmethod
    def generate_password(length=12):
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choices(chars, k=length))
        return password

    def __hash_passwords(self, password):
        ph = PasswordHasher()
        return ph.hash(password)

    def create_co_worker(self, email, first_name, last_name, phone, team, session):

        # Générer un mot de passe basique, l'utilisateur devra le changer
        password = team.lower()

        # Hachage du mot de passe
        hashed_password = self.__hash_passwords(password)

        # Récupérer l'id de l'équipe
        team_id = session.query(Team).filter_by(name=team).first().id

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
        session.add(new_user)
        session.commit()

        self.view.success_message(first_name, last_name)

    def display_co_workers(self):
        co_workers = self.session.query(User).all()
        self.view.show_co_workers(co_workers)
        return co_workers

    def get_co_workers_ids(self, co_workers):
        co_workers_ids = []
        for co_worker in co_workers:
            co_workers_ids.append(co_worker.id)
        return co_workers_ids

    def update_co_worker(self):
        # Afficher tous les événements de l'utilisateur support
        co_workers = self.display_co_workers()
        # Récupérer tous les ids des événements
        co_workers_ids = self.get_co_workers_ids(co_workers)
        # Demander de choisir un événement
        id = self.view.get_updating_co_worker(co_workers_ids)
        # Récupérer l'objet dans la base
        co_worker = self.session.query(User).filter(User.id == id).first()
        # Récupérer toutes les équipes
        teams = (self.session.query(Team).all())
        # Le modifier
        co_worker = self.view.get_co_worker_new_data(co_worker, teams)
        # Le mettre en base
        self.session.commit()




