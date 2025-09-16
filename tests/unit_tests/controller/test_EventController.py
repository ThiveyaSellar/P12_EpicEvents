from types import SimpleNamespace

import pytest
from unittest.mock import MagicMock, patch


from controller.EventController import EventController

@pytest.fixture
def event_controller():
    mock_session = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.obj = {
        "session": mock_session,
        "SECRET_KEY": "fake_secret_key"
    }
    controller = EventController(ctx=mock_ctx)
    controller.view = MagicMock()
    controller.session = mock_session
    return controller

class TestEventController:

    def test_update_support_events_success(self,event_controller):
        # 1️⃣ Préparer l'événement initial
        event1 = MagicMock()
        event1.id = 1
        event1.name = "Event1"
        event1.start_date = "2025-01-01"
        event1.end_date = "2025-01-02"
        event1.address = "Addr"
        event1.nb_attendees = 10
        event1.notes = "Note"
        event_controller.display_support_events = MagicMock(
            return_value=[event1])

        # 2️⃣ L'utilisateur choisit cet événement
        event_controller.view.get_updating_event = MagicMock(return_value=1)

        # 3️⃣ Mock de la récupération de l'événement en DB
        event_controller.session.query().filter().first.return_value = event1

        # 4️⃣ Préparer l'événement mis à jour (nouvelles données)
        updated_event = MagicMock()
        updated_event.name = "Event1 Updated"
        updated_event.start_date = "2025-01-01"
        updated_event.end_date = "2025-01-02"
        updated_event.address = "Addr"
        updated_event.nb_attendees = 12
        updated_event.notes = "Updated Note"
        event_controller.view.get_event_new_data = MagicMock(
            return_value=updated_event)

        # 5️⃣ Validation OK (pas d'erreurs)
        event_controller.validate_event_data = MagicMock(return_value=[])

        # 6️⃣ Patcher `commit_to_db` et `get_ids`
        with patch("controller.EventController.commit_to_db") as mock_commit, \
                patch("controller.EventController.get_ids",
                      side_effect=lambda events: [e.id for e in events]):
            # Exécuter la fonction
            event_controller.update_support_events()

        # 7️⃣ Vérifier que l'enregistrement a été appelé
        mock_commit.assert_called_once()

        # 8️⃣ Vérifier que le message de succès a été affiché
        event_controller.view.message_event_updated.assert_called_once()

    from unittest.mock import MagicMock, patch

    @patch("controller.EventController.get_ids", return_value=[1])
    def test_update_support_events_invalid_data(self, mock_get_ids,
                                                event_controller):
        # 1. Mock affichage des events
        event1 = MagicMock()
        event1.id = 1
        event_controller.display_support_events = MagicMock(
            return_value=[event1])

        # 2. L’utilisateur choisit l’événement valide
        event_controller.view.get_updating_event = MagicMock(return_value=1)

        # 3. Mock session pour retourner l’event
        event_controller.session.query().filter().first.return_value = event1

        # 4. Mock get_event_new_data avec des données invalides
        invalid_event = MagicMock()
        invalid_event.name = ""
        invalid_event.start_date = "bad_date"
        invalid_event.end_date = "bad_date"
        invalid_event.address = ""
        invalid_event.nb_attendees = -5
        invalid_event.notes = "note"
        event_controller.view.get_event_new_data = MagicMock(
            return_value=invalid_event)

        # 5. Appeler la méthode
        event_controller.update_support_events()

        # 6. Vérifier que le message d’erreur est appelé
        event_controller.view.message_updating_event_failed.assert_called_once()

    @patch("controller.EventController.get_ids")
    @patch("controller.EventController.commit_to_db")
    def test_create_event_for_my_client_success(self, mock_commit,
                                                mock_get_ids,
                                                event_controller):
        # 1. Mock clients et leur sélection
        client1 = MagicMock()
        client1.id = 1
        event_controller.view.select_client_for_event = MagicMock(
            return_value=1)

        # 2. Mock UserController pour retourner clients et support
        user_controller_mock = MagicMock()
        user_controller_mock.get_my_clients.return_value = [client1]
        support1 = MagicMock()
        support1.id = 10
        user_controller_mock.get_employees_from_team.return_value = [support1]

        # Patch temporaire de UserController pour utiliser notre mock
        with patch("controller.EventController.UserController",
                   return_value=user_controller_mock):
            # 3. Mock des données de l’event
            event_data = {
                "name": "Event Test",
                "start_date": "2025-09-15",
                "end_date": "2025-09-16",
                "address": "123 Street",
                "nb_attendees": 50,
                "notes": "Test notes"
            }
            event_controller.view.get_new_event_data = MagicMock(
                return_value=event_data)
            event_controller.validate_event_data = MagicMock(return_value=[])

            # 4. Mock sélection du support
            event_controller.view.select_support_for_event = MagicMock(
                return_value=10)

            # 5. Appel de la méthode
            event_controller.create_event_for_my_client()

            # 6. Assertions
            event_controller.session.add.assert_called_once()
            mock_commit.assert_called_once()
            event_controller.view.message_event_added.assert_called_once()

    @patch("controller.EventController.get_ids")
    @patch("controller.EventController.commit_to_db")
    def test_add_support_collab_to_event_success(self, mock_commit,
                                                 mock_get_ids,
                                                 event_controller):
        # 1. Mock events sans support
        event = MagicMock()
        event.id = 1
        event_controller.list_events_without_support = MagicMock(
            return_value=[event])
        event_controller.view.get_updating_event = MagicMock(return_value=1)

        # Patch get_ids pour retourner les ids
        mock_get_ids.return_value = [1]

        # 2. Mock session.query pour renvoyer notre event
        event_controller.session.query().filter().first.return_value = event

        # 3. Mock UserController et support selection
        user_controller_mock = MagicMock()
        support_emp = MagicMock()
        support_emp.id = 10
        user_controller_mock.get_employees_from_team.return_value = [
            support_emp]
        user_controller_mock.view.choose_support_collab = MagicMock(
            return_value=10)

        with patch("controller.EventController.UserController",
                   return_value=user_controller_mock):
            event_controller.add_support_collab_to_event()

            # Assertions
            assert event.support_id == 10
            mock_commit.assert_called_once()

    @patch("controller.EventController.get_ids")
    @patch("controller.EventController.commit_to_db")
    def test_add_support_collab_to_event_not_found(self, mock_commit,
                                                   mock_get_ids,
                                                   event_controller):
        # 1. Mock events sans support
        event = MagicMock()
        event.id = 1
        event_controller.list_events_without_support = MagicMock(
            return_value=[event])
        # L'utilisateur choisit un id inexistant
        event_controller.view.get_updating_event = MagicMock(return_value=999)

        # Patch get_ids pour retourner les ids valides
        mock_get_ids.return_value = [1]

        # Mock session.query pour renvoyer None pour cet id
        event_controller.session.query().filter().first.return_value = None

        # Exécuter la méthode
        event_controller.add_support_collab_to_event()

        # Vérifier que le message d'erreur est appelé
        event_controller.view.message_event_not_found.assert_called_once()
        # commit ne doit pas être appelé
        mock_commit.assert_not_called()

    def test_get_event_ids_without_contract(self, event_controller):
        event_with_contract = MagicMock()
        event_with_contract.id = 1
        event_with_contract.contract_id = 123

        event_without_contract = MagicMock()
        event_without_contract.id = 2
        event_without_contract.contract_id = None

        events = [event_with_contract, event_without_contract]

        result = event_controller.get_event_ids_without_contract(events)

        assert result == [2]
