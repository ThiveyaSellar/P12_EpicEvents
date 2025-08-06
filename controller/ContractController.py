from datetime import date

from models import Contract, Event, User, Team
from views.ContractView import ContractView
from views.UserView import UserView
from controller.EventController import EventController
from types import SimpleNamespace

class ContractController:

    def __init__(self, ctx):
        self.view = ContractView()
        self.session = ctx.obj["session"]
        self.SECRET_KEY = ctx.obj["SECRET_KEY"]

    def display_all_contracts(self):
        contracts = self.session.query(Contract).all()
        self.view.show_contracts(contracts)
        return contracts

    def get_contracts_ids(self, contracts):
        contract_ids = []
        for contract in contracts:
            contract_ids.append(int(contract.id))
        return contract_ids

    def create_contract(self):
        # Récupérer les événements et les clients associés
        ctx = {"session": self.session, "SECRET_KEY": self.SECRET_KEY}
        event_controller = EventController(SimpleNamespace(obj=ctx))
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
        if not event or not event.client or not event.client.commercial:
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

        self.view.message_contract_added()

    def update_contract(self):
        # Afficher tous les contrats
        contracts = self.display_all_contracts()
        if not contracts:
            self.view.message_no_contract()
            return
        # Récupérer tous les ids des contracts
        contracts_ids = self.get_contracts_ids(contracts)
        # Demander de choisir un contrat
        id = self.view.get_updating_contract(contracts_ids)
        if not id:
            return
        # Récupérer l'objet dans la base
        contract = self.session.query(Contract).filter(Contract.id == id).first()
        # Récupérer tous les commerciaux
        sales_rep = (
            self.session.query(User)
                .join(User.team)
                .filter(Team.name == "Commercial")
                .all()
        )
        # Le modifier
        contract = self.view.get_contract_new_data(contract, sales_rep)
        # Le mettre en base
        self.session.commit()

    def list_unpaid_contracts(self):
        unpaid_contracts = self.session.query(Contract).filter(Contract.remaining_amount!=0).all()
        self.view.show_contracts(unpaid_contracts)

    def list_unsigned_contracts(self):
        # Récupérer les contrats sans signature dans la base de données
        unsigned_contracts = self.session.query(Contract).filter_by(is_signed=False).all()
        # Afficher les contrats non signés
        self.view.show_contracts(unsigned_contracts)