from controller.ClientController import ClientController
from controller.UserController import UserController
from models import Event, Team
from views.EventView import EventView
from utils.TokenManagement import TokenManagement
from utils.helpers import get_ids
from types import SimpleNamespace


class EventController:

    def __init__(self, ctx):
        self.view = EventView()
        self.session = ctx.obj["session"]
        self.SECRET_KEY = ctx.obj["SECRET_KEY"]

    def get_all_events(self):
        events = self.session.query(Event).all()
        self.view.show_events(events)
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
        ctx = {"session": self.session, "SECRET_KEY": self.SECRET_KEY}
        user_controller = UserController(SimpleNamespace(obj=ctx))
        clients = user_controller.get_my_clients()
        clients_ids = get_ids(clients)
        # Demander de choisir un client par l'id
        client_id = self.view.select_client_for_event(clients_ids)
        event_data = self.view.get_new_event_data()
        support_agents = user_controller.get_employees_from_team("Support")
        support_ids = get_ids(support_agents)
        support_id = self.view.select_support_for_event(support_ids)

        # Choisir et assigner une personne du support
        new_event = Event(
            name=event_data["name"],
            start_date=event_data["start_date"],
            end_date=event_data["end_date"],
            address=event_data["address"],
            nb_attendees=event_data["nb_attendees"],
            notes=event_data["notes"],
            client_id=client_id,
            support_id=support_id
        )
        self.session.add(new_event)
        self.session.commit()

    def list_events_without_support(self):
        # Chercher les événements en base sans collaborateur
        events_without_support = self.session.query(Event).filter(Event.support_id == None).all()
        # Afficher les événements
        self.view.show_events(events_without_support)
        return events_without_support

    def list_events_without_contract(self):
        # Chercher les événements en base sans collaborateur
        events_without_contract = self.session.query(Event).filter(Event.contract_id == None).all()
        # Afficher les événements
        self.view.show_events(events_without_contract)

    def add_support_collab_to_event(self):
        # Afficher les événements sans supports
        events = self.list_events_without_support()
        events_ids = get_ids(events)
        # Demander l'événement sans support à modifier
        event_id = self.view.get_updating_event(events_ids)
        event = self.session.query(Event).filter(Event.id == event_id).first()
        if not event:
            self.view.message_event_not_found()
            return
        # Afficher les collaborateurs support
        ctx = {"session": self.session, "SECRET_KEY": self.SECRET_KEY}
        user_controller = UserController(SimpleNamespace(obj=ctx))
        support_employees = user_controller.get_employees_from_team("Support")
        support_id = user_controller.view.choose_support_collab(support_employees)

        event.support_id = support_id
        self.session.commit()






