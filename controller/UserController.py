import random
import string
from argon2 import PasswordHasher
from sqlalchemy import func

from models import User, Team, Client, Contract, Event
from utils.TokenManagement import TokenManagement
from utils.helpers import get_ids
from views.UserView import UserView

class UserController:

    def __init__(self,ctx):
        self.view = UserView()
        self.session = ctx.obj["session"]
        self.SECRET_KEY = ctx.obj["SECRET_KEY"]

    @staticmethod
    def generate_password(length=12):
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choices(chars, k=length))
        return password

    def __hash_passwords(self, password):
        ph = PasswordHasher()
        return ph.hash(password)

    def create_co_worker(self, email, first_name, last_name, phone, team):

        # Générer un mot de passe basique, l'utilisateur devra le changer
        password = team.lower()

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

    def display_co_workers(self):
        co_workers = self.session.query(User).all()
        self.view.show_co_workers(co_workers)
        return co_workers

    def select_co_worker(self, action_name):
        # Afficher tous les collaborateurs
        co_workers = self.display_co_workers()
        # Récupérer les IDs
        co_workers_ids = get_ids(co_workers)
        # Demander de choisir un collaborateur selon l'action
        id = self.view.get_co_worker(co_workers_ids, action_name)
        # Retourner l'objet User
        return self.session.query(User).filter(User.id == id).first()

    def update_co_worker(self):
        co_worker = self.select_co_worker("update")
        # Récupérer toutes les équipes
        teams = (self.session.query(Team).all())
        # Le modifier
        co_worker = self.view.get_co_worker_new_data(co_worker, teams)
        # Le mettre en base
        self.session.commit()

    def update_co_worker_related_data(self, co_worker):
        if co_worker.team == "Commercial":
            clients = self.session.query(Client).filter(
                Client.commercial_id == co_worker.id).all()
            for client in clients:
                client.commercial_id = None
            contracts = self.session.query(Contract).filter(
                Contract.commercial_id == co_worker.id).all()
            for contract in contracts:
                contract.commercial_id = None
        elif co_worker.team == "Support":
            events = self.session.query(Event).filter(
                Event.commercial_id == co_worker.id).all()
            for event in events:
                event.commercial_id = None
        elif co_worker.team == "Gestion":
            pass


    def delete_co_worker(self):
        co_worker = self.select_co_worker("delete")
        if co_worker:
            # Mettre à jour les colonnes dans les autres tables
            self.update_co_worker_related_data(co_worker)
            # Supprimer le co-worker
            self.session.delete(co_worker)
            self.session.commit()
        if not self.session.query(User).filter(co_worker.id == User.id).first():
            self.view.message_co_worker_deleted()
        else:
            self.view.message_inexistent_co_worker()

    def get_my_clients(self):
        "As a sale representative"
        user = TokenManagement.get_connected_user(self.session,
                                                  self.SECRET_KEY)
        clients = self.session.query(Client).filter(Client.commercial_id == user.id).all()
        self.view.show_my_clients(clients)
        return clients

    def get_employees_from_team(self,team):
        employees = self.session.query(User).join(Team).filter(func.lower(Team.name) == team.lower()).all()
        return employees




