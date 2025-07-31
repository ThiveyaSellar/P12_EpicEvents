
from models import Event
from views.EventView import EventView
from utils.TokenManagement import TokenManagement

class EventController:

    def __init__(self,session, SECRET_KEY):
        self.view = EventView()
        self.session = session
        self.SECRET_KEY = SECRET_KEY

    def display_all_events(self, session):
        events = session.query(Event).all()
        self.view.show_all_events(events)

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




