from controller.ClientController import ClientController
from controller.UserController import UserController
from models import Event
from views.EventView import EventView
from utils.TokenManagement import TokenManagement

class EventController:

    def __init__(self, ctx):
        self.view = EventView()
        self.session = ctx.obj["session"]
        self.SECRET_KEY = ctx.obj["SECRET_KEY"]

    def get_all_events(self):
        events = self.session.query(Event).all()
        print(events)
        self.view.show_all_events(events)
        return events

    def display_support_events(self):
        # Les événements attribués à l'utilisateur dans l'équipe support ?
        user = TokenManagement.get_connected_user(self.session, self.SECRET_KEY)
        events = self.session.query(Event).filter(Event.support.has(id=user.id)).all()
        self.view.show_support_events(events)
        return events

    def get_event_ids(self, events):
        event_ids = []
        for event in events:
            event_ids.append(event.id)
        return event_ids

    def get_event_ids_without_contract(self, events):
        event_ids = []
        for event in events:
            if event.contract_id is None:
                event_ids.append(event.id)
        return event_ids

    def update_support_events(self):
        # Afficher tous les événements de l'utilisateur support
        events = self.display_support_events()
        # Récupérer tous les ids des événements
        event_ids = self.get_event_ids(events)
        # Demander de choisir un événement
        id = self.view.get_updating_event(event_ids)
        # Récupérer l'objet dans la base
        event = self.session.query(Event).filter(Event.id==id).first()
        # Le modifier
        event = self.view.get_event_new_data(event)
        # Le mettre en base
        self.session.commit()

    def create_event_for_my_client(self):
        # Afficher mes clients
        user_controller = UserController(self.session, self.SECRET_KEY)
        clients = user_controller.get_my_clients()
        client_controller = ClientController(self.session, self.SECRET_KEY)
        clients_ids = client_controller.get_clients_ids(clients)
        client_id = self.view.select_client_for_event(clients_ids)
        event_data = self.view.get_new_event_data()
        # Créer la fonction ci-dessus
        # Par curiosité est-ce que tu te souviens où tu en étais ?

        exit()

        # Demander les données de l'événement

        # Afficher les personnes du support pouvant être affecté à l'événement

        # Choisir et assigner une personne du support

        # Créer l'objet

"""        event_controller = EventController(self.session, self.SECRET_KEY)
        # Afficher les événements avec le nom du client
        events = event_controller.get_all_events()
        event_ids = event_controller.get_event_ids_without_contract(events)
        if not event_ids:
            self.view.message_no_events_without_contracts()
            return
        # Choisir l'événement pour lequel je veux créer un contrat
        event_id = self.view.select_event_for_contract(event_ids)
        # Récupérer les informations du contrat
        contract_data = self.view.get_new_contract_data()
        # Récupérer le commercial associé à l'événement en récupérant le client
        event = next((e for e in events if e.id == event_id), None)
        if not event:
            self.view.message_invalid_event()
            return
        contract_data["commercial_id"] = event.client.commercial.id

        new_contract = Contract(
            total_amount=contract_data["total_amount"],
            remaining_amount=contract_data["remaining_amount"],
            creation_date=date.today(),
            is_signed=contract_data["is_signed"],
            commercial_id=contract_data["commercial_id"]
        )

        self.session.add(new_contract)
        self.session.commit()

        # Associer le contrat à l’événement
        event.contract_id = new_contract.id
        self.session.commit()

        self.view.message_contract_added()"""





