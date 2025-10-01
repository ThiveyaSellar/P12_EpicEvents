from datetime import date
from types import SimpleNamespace

from controller.UserController import UserController
from models import Client, User, Team
from views.ClientView import ClientView
from utils.TokenManagement import TokenManagement
from utils.helpers import (
    get_ids,
    check_field_and_length,
    check_email_field,
    check_phone_field,
)
from utils.db_helpers import commit_to_db

import logging

logger = logging.getLogger(__name__)


class ClientController:

    def __init__(self, ctx):
        self.view = ClientView()
        self.session = ctx.obj["session"]
        self.SECRET_KEY = ctx.obj["SECRET_KEY"]

    def get_all_clients(self):
        clients = self.session.query(Client).all()
        self.view.show_all_clients(clients)
        return clients

    @staticmethod
    def validate_client_data(data):
        errors = []
        check_field_and_length(data, "first_name", 100, errors)
        check_field_and_length(data, "last_name", 100, errors)
        check_field_and_length(data, "company", 100, errors)
        check_email_field(data, errors)
        check_phone_field(data, errors)
        return errors

    def create_client(self):
        client_data = self.view.get_new_client_data()
        # Valider les données saisies par l'utilisateur
        errors = self.validate_client_data(client_data)
        if errors:
            self.view.message_adding_client_failed(errors)
            return

        try:
            # Get current commercial user id
            user = TokenManagement.get_connected_user(
                self.session, self.SECRET_KEY
            )
            if user is None:
                self.view.message_adding_client_failed("User not connected.")
                return
        except Exception as e:
            self.view.message_adding_client_failed(
                f"Authentication error: {str(e)}"
            )
            logger.info(f"Authentication error: {str(e)}")
            return

        new_client = Client(
            first_name=client_data["first_name"],
            last_name=client_data["last_name"],
            email_address=client_data["email_address"],
            phone=client_data["phone"],
            company=client_data["company"],
            creation_date=date.today(),
            last_update=date.today(),
            commercial_id=user.id,
        )

        self.session.add(new_client)
        success = commit_to_db(
            self.session,
            self.view,
            success_callback=self.view.message_client_added,
            error_callback=self.view.message_adding_client_failed,
        )

        if not success:
            return

    def display_sales_clients(self):
        # Les événements attribués à l'utilisateur dans l'équipe support ?
        user = TokenManagement.get_connected_user(
            self.session, self.SECRET_KEY
        )
        clients = (
            self.session
            .query(Client)
            .filter(Client.commercial.has(id=user.id))
            .all()
        )
        self.view.show_sales_clients(clients)
        return clients

    def update_client(self):
        # Afficher tous les clients de l'utilisateur commercial
        clients = self.display_sales_clients()
        # Récupérer tous les ids des clients
        clients_ids = get_ids(clients)
        # Demander de choisir un client
        c_id = self.view.get_updating_client(clients_ids)
        if not c_id:
            return
        # Récupérer l'objet dans la base
        client = self.session.query(Client).filter(Client.id == c_id).first()
        # Récupérer tous les commerciaux
        sales_rep = (
            self.session.query(User)
            .join(User.team)
            .filter(Team.name == "Sales")
            .all()
        )
        # Le modifier
        client = self.view.get_client_new_data(client, sales_rep)
        data = {
            "first_name": client.first_name,
            "last_name": client.last_name,
            "email_address": client.email_address,
            "phone": client.phone,
            "company": client.company,
        }
        errors = self.validate_client_data(data)

        if errors:
            self.view.message_adding_client_failed(errors)
            return
        client.last_update = date.today()
        # Le mettre en base
        success = commit_to_db(
            self.session,
            self.view,
            success_callback=self.view.message_client_updated,
            error_callback=self.view.message_updating_client_failed,
        )
        if not success:
            return

    def add_sales_rep_collab_to_client(self):
        # Afficher les clients sans commerciaux
        clients = self.list_clients_without_sales_rep()
        if not clients:
            self.view.message_no_clients_available()
            return
        clients_ids = get_ids(clients)
        # Demander le client sans commercial à modifier
        client_id = self.view.get_updating_client(clients_ids)
        if not client_id:
            self.view.message_client_not_choosen()
            return
        client = self.session\
            .query(Client)\
            .filter(Client.id == client_id)\
            .first()
        if not client:
            self.view.message_client_not_found()
            return
        # Afficher les collaborateurs support
        ctx = {"session": self.session, "SECRET_KEY": self.SECRET_KEY}
        user_controller = UserController(SimpleNamespace(obj=ctx))
        sales_reps = user_controller.get_employees_from_team("Sales")
        if not sales_reps:
            user_controller.view.message_no_sales_rep_available()
            return
        sales_rep_id = user_controller.view.choose_support_collab(sales_reps)

        client.commercial_id = sales_rep_id
        commit_to_db(self.session, self.view)

    def list_clients_without_sales_rep(self):
        clients_without_sales_rep = (
            self.session
            .query(Client)
            .filter(Client.commercial_id.is_(None))
            .all()
        )
        self.view.show_all_clients(clients_without_sales_rep)
        return clients_without_sales_rep
