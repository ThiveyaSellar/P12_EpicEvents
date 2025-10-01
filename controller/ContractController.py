import logging
from datetime import date

from models import Contract, User, Team
from utils.TokenManagement import TokenManagement
from utils.helpers import get_ids
from utils.db_helpers import commit_to_db

from views.ContractView import ContractView
from controller.EventController import EventController
from types import SimpleNamespace

logger = logging.getLogger(__name__)


class ContractController:

    def __init__(self, ctx):
        self.view = ContractView()
        self.session = ctx.obj["session"]
        self.SECRET_KEY = ctx.obj["SECRET_KEY"]

    def list_contracts(self):
        contracts = self.session.query(Contract).all()
        if len(contracts) == 0:
            self.view.message_no_contract()
            return
        self.view.show_contracts(contracts)
        return contracts

    def validate_contract_data(self, data):
        # Vérifier les données dans le dictionnaire data
        errors = []
        total_amount = data.get("total_amount")
        if total_amount is None:
            errors.append("Total amount is required.")
        elif not isinstance(total_amount, int) or total_amount <= 0:
            errors.append("Total amount must be an int greater than 0.")

        remaining_amount = data.get("remaining_amount")
        if remaining_amount is not None:
            if not isinstance(remaining_amount, int) or remaining_amount < 0:
                errors.append("Remaining amount must be > 0.")
            elif remaining_amount > total_amount:
                errors.append("Remaining amount can't be > total amount.")

        """if "is_signed" not in data:
            errors.append("L'état de signature est obligatoire.")
        elif not isinstance(data["is_signed"], bool):
            errors.append("Le champ 'is_signed' doit être un booléen.")"""

        return errors

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
        errors = self.validate_contract_data(contract_data)
        if errors:
            self.view.message_adding_contract_failed(errors)
            return
        # Récupérer le commercial associé à l'événement en récupérant le client
        event = None
        for e in events:
            if e.id == event_id:
                event = e
                break

        if not event:
            self.view.message_invalid_event()
            return

        # Si pas de commercial associé au client
        # le commercial n'est pas attaché au contrat
        if event.client.commercial:
            contract_data["commercial_id"] = event.client.commercial_id
        else:
            contract_data["commercial_id"] = None

        new_contract = Contract(
            total_amount=contract_data["total_amount"],
            remaining_amount=contract_data["remaining_amount"],
            creation_date=date.today(),
            is_signed=False,
            commercial_id=contract_data["commercial_id"]
        )

        self.session.add(new_contract)
        commit_to_db(self.session, self.view)

        # Associer le contrat à l’événement
        event.contract_id = new_contract.id
        commit_to_db(self.session, self.view)

        self.view.message_contract_added()

    def list_unpaid_contracts(self):
        unpaid_contracts = (
            self.session
            .query(Contract)
            .filter(Contract.remaining_amount != 0)
            .all()
        )
        if not unpaid_contracts:
            self.view.message_no_contract()
            return
        self.view.show_contracts(unpaid_contracts)

    def list_unsigned_contracts(self):
        # Récupérer les contrats sans signature dans la base de données
        unsigned_contracts = (
            self.session
            .query(Contract)
            .filter_by(is_signed=False)
            .all()
        )
        if not unsigned_contracts:
            self.view.message_no_contract()
            return
        # Afficher les contrats non signés
        self.view.show_contracts(unsigned_contracts)

    def update_contract(self):
        # Si l'utilisateur est commercial afficher uniquement ses contrats
        # Sinon s'il est de l'équipe de gestion afficher tous les contrats
        user = TokenManagement.get_connected_user(self.session,
                                                  self.SECRET_KEY)
        # Vérifier qu'il est commercial, qu'il a le droit
        # Récupérer l'id de l'équipe du commercial
        sales_rep_team_id = self.session.query(Team).filter(
            Team.name == "Sales").first().id
        management_team_id = self.session.query(Team).filter(
            Team.name == "Management").first().id

        if user.team_id == sales_rep_team_id:
            # Chercher les contrats du commercial connecté dans la base
            contracts = self.session.query(Contract).filter(
                Contract.commercial_id == user.id).all()
            self.view.show_contracts(contracts)
        elif user.team_id == management_team_id:
            # Afficher tous les contrats
            contracts = self.list_contracts()
        else:
            self.view.message_action_not_permitted()
            return

        if not contracts:
            self.view.message_no_contract()
            return
        # Récupérer tous les ids des contracts
        contracts_ids = get_ids(contracts)
        # Demander de choisir un contrat
        id = self.view.get_updating_contract(contracts_ids)
        if not id:
            return
        # Récupérer l'objet dans la base
        contract = (
            self.session
            .query(Contract)
            .filter(Contract.id == id)
            .first()
        )
        if contract.is_signed:
            self.view.message_signed_no_update()
            return
        # Récupérer tous les commerciaux
        sales_rep = (
            self.session.query(User)
                .join(User.team)
                .filter(Team.name == "Sales")
                .all()
        )
        # Le modifier
        contract = self.view.get_contract_new_data(contract, sales_rep)
        data = {
            "total_amount": contract.total_amount,
            "remaining_amount": contract.remaining_amount,
            "commercial_id": contract.commercial_id
        }
        errors = self.validate_contract_data(data)
        is_commercial = data["commercial_id"] is not None
        if is_commercial and data["commercial_id"] not in get_ids(sales_rep):
            errors.append("Commercial_id is not valid.")
        if errors:
            self.view.message_updating_contract_failed(errors)
            return
        # Le mettre en base
        commit_to_db(self.session, self.view)
        self.view.message_contract_updated()

    def get_contracts_without_sign(self):
        contracts = (
            self.session
            .query(Contract)
            .filter(Contract.is_signed.is_(False))
            .all()
        )
        return contracts

    def sign_contract(self):
        # Afficher les contrats sans signatures
        contracts = self.get_contracts_without_sign()
        self.view.show_contracts(contracts)
        ids = get_ids(contracts)
        # Choisir un contrat
        id = self.view.get_signing_contract(ids)
        # Modifier le champ signature
        for contract in contracts:
            if contract.id == id:
                contract.is_signed = True
                break
        commit_to_db(self.session, self.view)
        # Journaliser
        logger.info(f"Contract {id} has been signed.")
