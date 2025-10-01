import string
import logging
import random
from argon2 import PasswordHasher

from models import User, Team, Client, Contract, Event
from utils.TokenManagement import TokenManagement
from utils.db_helpers import commit_to_db
from utils.helpers import (
    get_ids,
    check_email_field,
    check_field_and_length,
    check_phone_field,
    check_team_field,
)
from views.UserView import UserView


logger = logging.getLogger(__name__)


class UserController:

    def __init__(self, ctx):
        self.view = UserView()
        self.session = ctx.obj["session"]
        self.SECRET_KEY = ctx.obj["SECRET_KEY"]

    @staticmethod
    def generate_password(length=12):
        chars = string.ascii_letters + string.digits + string.punctuation
        password = "".join(random.choices(chars, k=length))
        return password

    @staticmethod
    def __hash_passwords(password):
        ph = PasswordHasher()
        return ph.hash(password)

    @staticmethod
    def validate_user_data(data):
        errors = []

        check_email_field(data, errors)
        check_field_and_length(data, "first_name", 100, errors)
        check_field_and_length(data, "last_name", 100, errors)
        check_phone_field(data, errors)
        check_team_field(data, errors)
        return errors

    def email_exists_in_db(self, email):
        user = self.session.query(User).filter_by(email_address=email).first()
        return user is not None

    def create_co_worker(self, email, first_name, last_name, phone, team):

        # Générer un mot de passe basique, l'utilisateur devra le changer
        password = team.lower()

        # Hachage du mot de passe
        hashed_password = self.__hash_passwords(password)

        # Récupérer l'id de l'équipe
        team_id = self.session.query(Team).filter_by(name=team).first().id

        user_data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "team": team,
        }

        # Vérifier que l'email est unique
        if self.email_exists_in_db(email):
            self.view.message_email_exists()
            return

        errors = self.validate_user_data(user_data)
        if errors:
            self.view.message_adding_co_worker_failed(errors)
            return

        # Création de l'utilisateur
        new_user = User(
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            email_address=email.strip().lower(),
            phone=phone,
            team_id=team_id,
        )

        # Enregistrement dans la base de données
        self.session.add(new_user)
        commit_to_db(self.session, self.view)

        logger.info(f"A new user is created: {first_name} {last_name}")

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
        co_w_id = self.view.get_co_worker(co_workers_ids, action_name)
        # Retourner l'objet User
        return self.session.query(User).filter(User.id == co_w_id).first()

    def update_co_worker(self):
        co_worker = self.select_co_worker("update")
        # Récupérer toutes les équipes
        teams = self.session.query(Team).all()
        # Le modifier
        co_worker = self.view.get_co_worker_new_data(co_worker, teams)
        data = {
            "first_name": co_worker.first_name,
            "last_name": co_worker.last_name,
            "email": co_worker.email_address,
            "phone": co_worker.phone,
            "team": co_worker.team.name,
        }
        errors = self.validate_user_data(data)
        if errors:
            self.view.message_updating_co_worker_failed(errors)
            return
        # Le mettre en base
        commit_to_db(self.session, self.view)
        logger.info(
            f"User {co_worker.first_name} {co_worker.last_name}\
            has been updated!"
        )

    def update_co_worker_related_data(self, co_worker):
        if co_worker.team == "Commercial":
            clients = (
                self.session.query(Client)
                .filter(Client.commercial_id == co_worker.id)
                .all()
            )
            for client in clients:
                client.commercial_id = None
            contracts = (
                self.session.query(Contract)
                .filter(Contract.commercial_id == co_worker.id)
                .all()
            )
            for contract in contracts:
                contract.commercial_id = None
        elif co_worker.team == "Support":
            events = (
                self.session
                .query(Event)
                .filter(Event.support_id == co_worker.id)
                .all()
            )
            for event in events:
                event.support_id = None
        elif co_worker.team == "Management":
            pass

    def delete_co_worker(self):
        co_worker = self.select_co_worker("delete")
        if co_worker:
            # Mettre à jour les colonnes dans les autres tables
            self.update_co_worker_related_data(co_worker)
            # Supprimer le co-worker
            self.session.delete(co_worker)
            commit_to_db(self.session, self.view)
            if not self.session.query(User).filter(co_worker.id == User.id)\
                    .first():
                self.view.message_co_worker_deleted()
                logger.info(
                    f"User {co_worker.first_name} {co_worker.last_name}\
                     has been deleted!"
                )
        else:
            self.view.message_inexistent_co_worker()

    def get_my_clients(self):
        user = TokenManagement.get_connected_user(
            self.session, self.SECRET_KEY
        )
        clients = (
            self.session
            .query(Client)
            .filter(Client.commercial_id == user.id)
            .all()
        )
        self.view.show_my_clients(clients)
        return clients

    def get_employees_from_team(self, team):
        employees = (
            self.session.query(User)
                .join(Team, User.team_id == Team.id)
                .filter(Team.name.ilike(team))
                .all()
        )

        return employees
