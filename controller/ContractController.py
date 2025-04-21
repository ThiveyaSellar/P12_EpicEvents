from models import Contract
from views.ContractView import ContractView

class ContractController:

    def __init__(self):
        self.view = ContractView()

    def display_all_contracts(self, session):
        contracts = session.query(Contract).all()
        self.view.show_all_contracts(contracts)