from datetime import date
from models import Client
from views.ClientView import ClientView
from utils.TokenManagement import TokenManagement


class ClientController:

    def __init__(self, session, SECRET_KEY):
        self.view = ClientView()
        self.session = session
        self.SECRET_KEY = SECRET_KEY

    def display_all_clients(self, session):
        clients = session.query(Client).all()
        self.view.show_all_clients(clients)

    def create_client(self):
        client_data = self.view.get_new_client_data()
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
        added_client = self.session.query(Client).filter_by(
            id=new_client.id).first()

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

    def get_clients_ids(self, clients):
        client_ids = []
        for client in clients:
            client_ids.append(client.id)
        return client_ids

    def update_client(self):
        # Afficher tous les clients de l'utilisateur commercial
        clients = self.display_sales_clients()
        # Récupérer tous les ids des événements
        clients_ids = self.get_clients_ids(clients)
        # Demander de choisir un client
        id = self.view.get_updating_client(clients_ids)
        # Récupérer l'objet dans la base
        client = self.session.query(Client).filter(Client.id == id).first()
        # Le modifier
        client = self.view.get_client_new_data(client)
        client.last_update=date.today()
        # Le mettre en base
        self.session.commit()