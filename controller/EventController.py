
from models import Event
from views.EventView import EventView
from utils.TokenManagement import TokenManagement

class EventController:

    def __init__(self):
        self.view = EventView()

    def display_all_events(self, session):
        events = session.query(Event).all()
        self.view.show_all_events(events)

    def display_support_events(self, session, SECRET_KEY):
        # Les événements attribués à l'utilisateur dans l'équipe support ?
        user = TokenManagement.get_connected_user(session, SECRET_KEY)
        events = session.query(Event).filter(Event.support.has(id=user.id)).all()
        self.view.show_support_events(events)