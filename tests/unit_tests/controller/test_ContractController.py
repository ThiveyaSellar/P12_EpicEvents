from types import SimpleNamespace

import pytest
from unittest.mock import MagicMock, patch


from controller.ContractController import ContractController

@pytest.fixture
def contract_controller():
    mock_session = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.obj = {
        "session": mock_session,
        "SECRET_KEY": "fake_secret_key"
    }
    controller = ContractController(ctx=mock_ctx)
    controller.view = MagicMock()
    controller.session = mock_session
    return controller

class TestContractController:

    @patch("controller.ContractController.commit_to_db")
    @patch("controller.ContractController.EventController")
    def test_create_contract_success(self, mock_event_ctrl, mock_commit,
                                     contract_controller):
        mock_event = MagicMock()
        mock_event.id = 1
        # mock_event.client.commercial = True
        mock_event.client.commercial_id = 42

        mock_event_ctrl.return_value.get_all_events.return_value = [mock_event]
        mock_event_ctrl.return_value.get_event_ids_without_contract.return_value = [
            1]

        contract_controller.view.select_event_for_contract.return_value = 1
        contract_controller.view.get_new_contract_data.return_value = {
            "total_amount": 1000,
            "remaining_amount": 200
        }

        contract_controller.create_contract()

        contract_controller.session.add.assert_called_once()
        mock_commit.assert_called()
        contract_controller.view.message_contract_added.assert_called_once()

    @patch("controller.ContractController.EventController")
    def test_create_contract_no_events(self, mock_event_ctrl, contract_controller):

        mock_event_ctrl.return_value.get_all_events.return_value = []
        mock_event_ctrl.return_value.get_event_ids_without_contract.return_value = []

        contract_controller.create_contract()

        contract_controller.view.message_no_events_without_contracts.assert_called_once()
        contract_controller.view.message_contract_added.assert_not_called()

    @patch("controller.ContractController.EventController")
    def test_create_contract_invalid_event(mock_event_ctrl,
                                           contract_controller):
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event_ctrl.return_value.get_all_events.return_value = [mock_event]
        mock_event_ctrl.return_value.get_event_ids_without_contract.return_value = [
            1]

        contract_controller.view.select_event_for_contract.return_value = 999  # id inexistant

        contract_controller.create_contract()

        contract_controller.view.message_invalid_event.assert_called_once()

    @patch("controller.ContractController.EventController")
    def test_create_contract_invalid_event(self, mock_event_ctrl,
                                           contract_controller):
        # Crée un event avec un id réel
        mock_event = SimpleNamespace(id=1, client=MagicMock())

        # EventController renvoie cet event
        mock_event_ctrl.return_value.get_all_events.return_value = [mock_event]
        mock_event_ctrl.return_value.get_event_ids_without_contract.return_value = [
            1]

        # L'utilisateur choisit un id qui n'existe pas
        contract_controller.view.select_event_for_contract.return_value = 999

        # On s'assure que le contrat est "valide" pour passer le check
        contract_controller.view.get_new_contract_data.return_value = {
            "total_amount": 1000,
            "remaining_amount": 500
        }
        patcher = patch.object(contract_controller, "validate_contract_data",
                               return_value=[])
        patcher.start()

        contract_controller.create_contract()

        contract_controller.view.message_invalid_event.assert_called_once()
        patcher.stop()

    @patch("controller.ContractController.EventController")
    def test_create_contract_invalid_data(self, mock_event_ctrl,
                                          contract_controller):
        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.client.commercial = True
        mock_event.client.commercial_id = 42

        mock_event_ctrl.return_value.get_all_events.return_value = [mock_event]
        mock_event_ctrl.return_value.get_event_ids_without_contract.return_value = [
            1]

        contract_controller.view.select_event_for_contract.return_value = 1
        contract_controller.view.get_new_contract_data.return_value = {
            "total_amount": -100}

        contract_controller.create_contract()

        contract_controller.view.message_adding_contract_failed.assert_called_once()

    @patch("controller.ContractController.TokenManagement.get_connected_user")
    def test_update_contract_no_permission(self, mock_get_user, contract_controller):
        mock_get_user.return_value = MagicMock(team_id=999)
        contract_controller.update_contract()
        contract_controller.view.message_action_not_permitted.assert_called_once()

    @patch("controller.ContractController.TokenManagement.get_connected_user")
    def test_update_contract_no_contracts(self, mock_get_user, contract_controller):
        mock_get_user.return_value = MagicMock(team_id=1, id=10)
        # Simule équipe Commercial
        contract_controller.session.query().filter().first().id = 1
        contract_controller.session.query().filter().all.return_value = []
        contract_controller.update_contract()
        contract_controller.view.message_no_contract.assert_called_once()

    @patch("controller.ContractController.TokenManagement.get_connected_user")
    def test_update_contract_signed_contract(self, mock_get_user,
                                             contract_controller):
        # Simuler utilisateur Commercial
        mock_get_user.return_value = MagicMock(team_id=1, id=10)

        # Mock équipe Commercial et Gestion
        team_commercial = MagicMock()
        team_commercial.id = 1
        team_gestion = MagicMock()
        team_gestion.id = 2

        # Mock contrat déjà signé
        signed_contract = MagicMock()
        signed_contract.id = 42
        signed_contract.is_signed = True  # forcer un booléen explicite

        # Configurer les mocks du session.query()
        contract_controller.session.query().filter().first.side_effect = [
            team_commercial,  # premier appel -> Commercial
            team_gestion,  # deuxième appel -> Gestion
            signed_contract  # troisième appel -> contrat signé
        ]
        contract_controller.session.query().filter().all.return_value = [
            signed_contract]

        # Simuler choix utilisateur
        contract_controller.view.get_updating_contract.return_value = 42

        # Exécuter la fonction
        contract_controller.update_contract()

        # Vérifier que le message attendu a été affiché
        contract_controller.view.message_signed_no_update.assert_called_once()

    @patch("controller.ContractController.TokenManagement.get_connected_user")
    def test_update_contract_user_cancels(self, mock_get_user,
                                          contract_controller):
        mock_get_user.return_value = MagicMock(team_id=1, id=10)

        team_commercial = MagicMock()
        team_commercial.id = 1
        team_gestion = MagicMock()
        team_gestion.id = 2
        contract = MagicMock()
        contract.id = 42
        contract.is_signed = False

        contract_controller.session.query().filter().first.side_effect = [
            team_commercial,
            team_gestion,
            contract
        ]
        contract_controller.session.query().filter().all.return_value = [
            contract]

        # L’utilisateur annule la sélection
        contract_controller.view.get_updating_contract.return_value = None

        contract_controller.update_contract()

        contract_controller.view.message_signed_no_update.assert_not_called()
        contract_controller.view.message_contract_updated.assert_not_called()

    @patch("controller.ContractController.TokenManagement.get_connected_user")
    def test_update_contract_signed_contract(self, mock_get_user,
                                             contract_controller):
        mock_get_user.return_value = MagicMock(team_id=1, id=10)

        team_commercial = MagicMock()
        team_commercial.id = 1
        team_gestion = MagicMock()
        team_gestion.id = 2
        signed_contract = MagicMock()
        signed_contract.id = 42
        signed_contract.is_signed = True

        contract_controller.session.query().filter().first.side_effect = [
            team_commercial,
            team_gestion,
            signed_contract
        ]
        contract_controller.session.query().filter().all.return_value = [
            signed_contract]
        contract_controller.view.get_updating_contract.return_value = 42

        contract_controller.update_contract()

        contract_controller.view.message_signed_no_update.assert_called_once()

    @patch("controller.ContractController.TokenManagement.get_connected_user")
    def test_update_contract_validation_errors(self, mock_get_user,
                                               contract_controller):
        mock_get_user.return_value = MagicMock(team_id=1, id=10)

        team_commercial = MagicMock()
        team_commercial.id = 1
        team_gestion = MagicMock()
        team_gestion.id = 2
        contract = MagicMock()
        contract.id = 42
        contract.is_signed = False

        contract_controller.session.query().filter().first.side_effect = [
            team_commercial,
            team_gestion,
            contract
        ]
        contract_controller.session.query().filter().all.return_value = [
            contract]
        contract_controller.view.get_updating_contract.return_value = 42

        updated_contract = MagicMock()
        updated_contract.total_amount = 1000
        updated_contract.remaining_amount = 500
        updated_contract.commercial_id = 123

        # Patch sur l'instance
        contract_controller.view.get_contract_new_data = MagicMock(
            return_value=updated_contract)
        contract_controller.validate_contract_data = MagicMock(
            return_value=["Invalid data"])

        contract_controller.update_contract()

        contract_controller.view.message_updating_contract_failed.assert_called_once()

    @patch("controller.ContractController.TokenManagement.get_connected_user")
    def test_update_contract_success(self, mock_get_user, contract_controller):
        mock_get_user.return_value = MagicMock(team_id=1, id=10)

        # Mocks équipes et contrat
        team_commercial = MagicMock(id=1)
        team_gestion = MagicMock(id=2)
        contract = MagicMock(id=42, is_signed=False)

        contract_controller.session.query().filter().first.side_effect = [
            team_commercial,
            team_gestion,
            contract
        ]
        contract_controller.session.query().filter().all.return_value = [
            contract]
        contract_controller.view.get_updating_contract.return_value = 42

        # Contrat mis à jour
        updated_contract = MagicMock(total_amount=1000, remaining_amount=500,
                                     commercial_id=123)
        contract_controller.view.get_contract_new_data = MagicMock(
            return_value=updated_contract)
        contract_controller.validate_contract_data = MagicMock(return_value=[])

        # Mock des commerciaux pour valider commercial_id
        sales_rep_mock = MagicMock(id=123)
        contract_controller.session.query().join().filter().all.return_value = [
            sales_rep_mock]

        # Patch commit
        with patch(
                "controller.ContractController.commit_to_db") as mock_commit:
            contract_controller.update_contract()

        mock_commit.assert_called_once()
        contract_controller.view.message_contract_updated.assert_called_once()