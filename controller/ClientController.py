from models import Client
from views.ClientView import ClientView

class ClientController:

    def __init__(self):
        self.view = ClientView()

    def display_all_clients(self, session):
        clients = session.query(Client).all()
        self.view.show_all_clients(clients)


