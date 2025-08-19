from datetime import date
from models import Client, User, Team
from views.ClientView import ClientView
from utils.TokenManagement import TokenManagement
from utils.helpers import get_ids, check_field_and_length, check_email_field, \
    check_phone_field


class ClientController:

    def __init__(self, ctx):
        self.view = ClientView()
        self.session = ctx.obj["session"]
        self.SECRET_KEY = ctx.obj["SECRET_KEY"]

    def get_all_clients(self):
        clients = self.session.query(Client).all()
        self.view.show_all_clients(clients)
        return clients

    def validate_client_data(self, data):
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
        # Get current commercial user id
        user = TokenManagement.get_connected_user(self.session,
                                                  self.SECRET_KEY)

        new_client = Client(
            first_name=client_data["first_name"],
            last_name=client_data["last_name"],
            email_address=client_data["email_address"],
            phone=client_data["phone"],
            company=client_data["company"],
            creation_date=date.today(),
            last_update=date.today(),
            commercial_id=user.id
        )
        self.session.add(new_client)
        self.session.commit()
        # Vérification si le client a été ajouté
        added_client = self.session.query(Client).filter_by(id=new_client.id).first()

        if added_client:
            self.view.message_client_added()
        else:
            self.view.message_adding_client_failed()

    def display_sales_clients(self):
        # Les événements attribués à l'utilisateur dans l'équipe support ?
        user = TokenManagement.get_connected_user(self.session,
                                                  self.SECRET_KEY)
        clients = self.session.query(Client).filter(
            Client.commercial.has(id=user.id)).all()
        self.view.show_sales_clients(clients)
        return clients

    def update_client(self):
        # Afficher tous les clients de l'utilisateur commercial
        clients = self.display_sales_clients()
        # Récupérer tous les ids des clients
        clients_ids = get_ids(clients)
        # Demander de choisir un client
        id = self.view.get_updating_client(clients_ids)
        if not id:
            return
        # Récupérer l'objet dans la base
        client = self.session.query(Client).filter(Client.id == id).first()
        # Récupérer tous les commerciaux
        sales_rep = (
            self.session.query(User)
                .join(User.team)
                .filter(Team.name == "Commercial")
                .all()
        )
        # Le modifier
        client = self.view.get_client_new_data(client, sales_rep)
        data = {
            "first_name": client.first_name,
            "last_name": client.last_name,
            "email_address": client.email_address,
            "phone": client.phone,
            "company": client.company
        }
        errors = self.validate_client_data(data)

        if errors:
            self.view.message_adding_client_failed(errors)
            return
        client.last_update=date.today()
        # Le mettre en base
        self.session.commit()