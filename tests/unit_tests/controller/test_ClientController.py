from datetime import date

import pytest
from controller.ClientController import ClientController
from unittest.mock import MagicMock, patch

from models import Client


@pytest.fixture
def client_controller():
    mock_session = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.obj = {"session": mock_session, "SECRET_KEY": "fake_secret_key"}
    controller = ClientController(ctx=mock_ctx)
    controller.view = MagicMock()
    return controller


class TestClientController:

    def test_get_all_clients(self, client_controller):
        fake_clients = [MagicMock(id=1), MagicMock(id=2)]

        client_controller.session.query.return_value.all.return_value = (
            fake_clients
        )

        result = client_controller.get_all_clients()

        client_controller.view.show_all_clients.assert_called_once_with(
            fake_clients
        )

        assert result == fake_clients

    def test_display_sales_clients(self, client_controller):
        fake_clients = [
            MagicMock(id=1, commercial_id=42),
            MagicMock(id=2, commercial_id=43),
        ]
        fake_user = MagicMock()
        fake_user.id = 42

        with patch(
            "controller.ClientController.TokenManagement.get_connected_user",
            return_value=fake_user,
        ):
            with patch.object(client_controller.session, "query") as mock_query:
                mock_filter = mock_query.return_value.filter
                mock_filter.return_value.all.return_value = fake_clients

                result = client_controller.display_sales_clients()

                assert result == fake_clients
                client_controller.view.show_sales_clients.assert_called_once_with(
                    fake_clients
                )

    def test_validate_client_data_missing_fields(self, client_controller):

        invalid_data = {
            "first_name": "",
            "last_name": None,
            "company": "Test",
            "email_address": "invalid-email",
        }

        errors = client_controller.validate_client_data(invalid_data)

        assert "The first_name field is required." in errors
        assert "The last_name field is required." in errors
        assert "Email is not valid or too long." in errors

    def test_validate_client_data_valid(self, client_controller):

        valid_data = {
            "first_name": "Abc",
            "last_name": "DEF",
            "company": "Test",
            "email_address": "abc@epicevents.com",
            "phone": "0102030405",
        }

        errors = client_controller.validate_client_data(valid_data)

        assert errors == []

    def test_create_client_success(self, client_controller):
        client_data = {
            "first_name": "Abc",
            "last_name": "DEF",
            "company": "Test",
            "email_address": "abc@epicevents.com",
            "phone": "0102030405",
        }

        # Mock pour remplacer la méthode de la vue récupèrant les données d'un client
        client_controller.view.get_client_new_data.return_value = client_data

        # Mock TokenManagement pour retourner un utilisateur avec un id
        fake_user = MagicMock()
        fake_user.id = 42

        with patch(
            "controller.ClientController.TokenManagement.get_connected_user",
            return_value=fake_user,
        ):
            # Mock commit_to_db
            with patch("controller.ClientController.commit_to_db") as mock_commit:
                # Simuler le commit : appeler callback succès
                def commit_effect(session, view, success_callback, error_callback):
                    success_callback()

                mock_commit.side_effect = commit_effect

                client_controller.session.query.return_value.filter_by.return_value.first.return_value = Client(
                    **client_data,
                    id=1,
                    commercial_id=42,
                    creation_date=date.today(),
                    last_update=date.today()
                )

                client_controller.validate_client_data = MagicMock(return_value=[])

                client_controller.create_client()

                assert client_controller.view.get_new_client_data.called

                client_controller.session.add.assert_called_once()

                assert client_controller.view.message_client_added.called

    def test_create_client_fails(self, client_controller):
        invalid_data = {
            "first_name": "",
            "last_name": "DEF",
            "company": "Test",
            "email_address": "abc@epicevents.com",
            "phone": "0102030405",
        }

        # Simuler la vue qui récupère les données
        client_controller.view.get_client_new_data.return_value = invalid_data

        # Simuler la fonction de validation des données
        errors = ["The first_name field is required."]
        client_controller.validate_client_data = MagicMock(return_value=errors)

        client_controller.create_client()

        # Vérifier que le message d'échec ait été affiché
        client_controller.view.message_adding_client_failed.assert_called_once_with(
            errors
        )

        # Vérifier que la fonction de commit en base n'ait été appelé
        assert not client_controller.session.add.called

    def test_create_client_commit_failure(self, client_controller):
        client_data = {
            "first_name": "Abc",
            "last_name": "DEF",
            "company": "Test",
            "email_address": "abc@epicevents.com",
            "phone": "0102030405",
        }

        client_controller.view.get_new_client_data.return_value = client_data

        client_controller.validate_client_data = MagicMock(return_value=[])

        fake_user = MagicMock()
        fake_user.id = 43
        with patch(
            "controller.ClientController.TokenManagement.get_connected_user",
            return_value=fake_user,
        ):
            with patch("controller.ClientController.commit_to_db") as mock_commit:

                def commit_effect(session, view, success_callback, error_callback):
                    error_callback("Simulated commit failure")

                mock_commit.side_effect = commit_effect
                client_controller.create_client()

                # client_controller.view.message_adding_client_failed.assert_called_with("Simulated commit failure")
                client_controller.view.message_adding_client_failed.assert_called()
                assert not client_controller.view.message_client_added.called
                assert client_controller.session.add.called

    def test_create_client_no_connected_user(self, client_controller):
        client_data = {
            "first_name": "Abc",
            "last_name": "DEF",
            "company": "Test",
            "email_address": "abc@epicevents.com",
            "phone": "0102030405",
        }

        client_controller.view.get_client_new_data.return_value = client_data
        client_controller.validate_client_data = MagicMock(return_value=[])

        with patch(
            "controller.ClientController.TokenManagement.get_connected_user",
            return_value=None,
        ):
            client_controller.create_client()

            client_controller.view.message_adding_client_failed.assert_called()
            assert not client_controller.session.add.called

    def test_create_client_get_connected_user_exception(self, client_controller):
        client_data = {
            "first_name": "Abc",
            "last_name": "DEF",
            "company": "Test",
            "email_address": "abc@epicevents.com",
            "phone": "0102030405",
        }

        client_controller.view.get_client_new_data.return_value = client_data
        client_controller.validate_client_data = MagicMock(return_value=[])

        with patch(
            "controller.ClientController.TokenManagement.get_connected_user",
            side_effect=Exception("User not connected."),
        ):
            client_controller.create_client()

            client_controller.view.message_adding_client_failed.assert_called()
            assert not client_controller.session.add.called

    def test_update_client_success(self, client_controller):
        fake_client = Client(
            id=1,
            first_name="Abc",
            last_name="DEF",
            company="Test",
            email_address="abc@epicevents.com",
            phone="0102030405",
        )
        client_controller.session.query.return_value.filter.return_value.first.return_value = (
            fake_client
        )

        # Simuler la sélection du client à mettre à jour
        client_controller.view.get_updating_client.return_value = 1

        # Simuler les nouvelles données récupérées
        fake_client.phone = "0123456789"

        client_controller.view.get_client_new_data.return_value = fake_client

        # client_controller.commit_to_db = MagicMock()

        fake_user = MagicMock()
        fake_user.id = 42

        with patch(
            "controller.ClientController.TokenManagement.get_connected_user",
            return_value=fake_user,
        ):
            # Mock commit_to_db
            with patch("controller.ClientController.commit_to_db") as mock_commit:
                # Simuler le commit : appeler callback succès
                def commit_effect(session, view, success_callback, error_callback):
                    success_callback()

                mock_commit.side_effect = commit_effect

                client_controller.validate_client_data = MagicMock(return_value=[])

                client_controller.update_client()

                assert client_controller.view.get_client_new_data.called
                assert fake_client.phone == "0123456789"
                client_controller.view.message_client_updated.assert_called_once()
                client_controller.view.message_not_found.assert_not_called()
                mock_commit.assert_called_once_with(
                    client_controller.session,
                    client_controller.view,
                    success_callback=client_controller.view.message_client_updated,
                    error_callback=client_controller.view.message_updating_client_failed,
                )

    def test_update_client_no_id(self, client_controller):

        # Simuler la sélection du client à mettre à jour
        client_controller.view.get_updating_client.return_value = None

        fake_user = MagicMock()
        fake_user.id = 42

        with patch(
            "controller.ClientController.TokenManagement.get_connected_user",
            return_value=fake_user,
        ), patch("controller.ClientController.commit_to_db") as mock_commit:

            client_controller.update_client()

            assert not client_controller.view.get_client_new_data.called
            mock_commit.assert_not_called()
            assert not client_controller.view.message_client_update.called
            assert not client_controller.view.message_updating_client_failed.called

    def test_update_client_validation_errors(self, client_controller):
        fake_client = Client(
            id=1,
            first_name="Abc",
            last_name="DEF",
            company="Test",
            email_address="abc@epicevents.com",
            phone="0102030405",
        )
        client_controller.session.query.return_value.filter.return_value.first.return_value = (
            fake_client
        )

        client_controller.view.get_updating_client.return_value = 1

        client_controller.view.get_client_new_data.return_value = fake_client

        client_controller.validate_client_data = MagicMock(
            return_value=["Email not valid."]
        )

        fake_user = MagicMock()
        fake_user.id = 42

        with patch(
            "controller.ClientController.TokenManagement.get_connected_user",
            return_value=fake_user,
        ), patch("controller.ClientController.commit_to_db") as mock_commit:
            client_controller.update_client()

            client_controller.view.message_adding_client_failed.assert_called_once_with(
                ["Email not valid."]
            )

            mock_commit.assert_not_called()

    def test_list_clients_without_sales_rep(self, client_controller):

        fake_clients_without_sales_rep = [
            MagicMock(id=1, commercial_id=None),
            MagicMock(id=2, commercial_id=None),
        ]

        client_controller.session.query.return_value.filter.return_value.all.return_value = (
            fake_clients_without_sales_rep
        )

        result = client_controller.list_clients_without_sales_rep()

        client_controller.view.show_all_clients.assert_called_once_with(
            fake_clients_without_sales_rep
        )

        assert result == fake_clients_without_sales_rep

    def test_add_sales_rep_no_clients(self, client_controller):

        fake_clients = []
        client_controller.list_clients_without_sales_rep = MagicMock(
            return_value=fake_clients
        )

        client_controller.add_sales_rep_collab_to_client()

        assert not client_controller.view.get_updating_client.called
        client_controller.view.message_no_clients_available.assert_called_once()

    def test_add_sales_rep_client_id_none(self, client_controller):
        fake_clients_without_sales_rep = [
            MagicMock(id=1, commercial_id=None),
            MagicMock(id=2, commercial_id=None),
        ]
        client_controller.list_clients_without_sales_rep = MagicMock(
            return_value=fake_clients_without_sales_rep
        )

        with patch.object(
            client_controller.view, "get_updating_client", return_value=None
        ):
            client_controller.add_sales_rep_collab_to_client()

        client_controller.view.message_client_not_choosen.assert_called_once()

    def test_add_sales_rep_client_not_found(self, client_controller):
        fake_clients_without_sales_rep = [
            MagicMock(id=1, commercial_id=None),
            MagicMock(id=2, commercial_id=None),
        ]
        client_controller.list_clients_without_sales_rep = MagicMock(
            return_value=fake_clients_without_sales_rep
        )

        client_controller.view.get_updating_client = MagicMock(
            result_value=fake_clients_without_sales_rep[0]
        )

        client_controller.session.query.return_value.filter.return_value.first.return_value = (
            None
        )

        client_controller.add_sales_rep_collab_to_client()

        client_controller.view.message_client_not_found.assert_called_once()

    def test_add_sales_rep_no_sales_reps(self, client_controller):

        fake_clients = [MagicMock(id=1), MagicMock(id=2)]
        client_controller.list_clients_without_sales_rep = MagicMock(
            return_value=fake_clients
        )

        client_controller.view.get_updating_client = MagicMock(
            return_value=fake_clients[0]
        )

        client_controller.session.query.return_value.filter.return_value.first.return_value = fake_clients[
            0
        ]

        with patch("controller.ClientController.UserController") as mock_user_ctrl_cls:
            mock_user_ctrl = MagicMock()
            mock_user_ctrl.get_employees_from_team.return_value = []
            mock_user_ctrl.view = MagicMock()
            mock_user_ctrl_cls.return_value = mock_user_ctrl

            client_controller.add_sales_rep_collab_to_client()

            mock_user_ctrl.view.choose_support_collab.assert_not_called()
            mock_user_ctrl.view.message_no_sales_rep_available.assert_called_once()

    def test_add_sales_rep_sales_rep_id_none(self, client_controller):
        fake_clients = [MagicMock(id=1, commercial_id=None)]
        client_controller.list_clients_without_sales_rep = MagicMock(
            return_value=fake_clients
        )

        client_controller.view.get_updating_client = MagicMock(
            return_value=fake_clients[0]
        )

        # Mock session.query.filter.first() pour retourner un client valide
        client_controller.session.query.return_value.filter.return_value.first.return_value = fake_clients[
            0
        ]

        with patch("controller.ClientController.UserController") as mock_user_ctrl_cls:
            mock_user_ctrl = MagicMock()
            mock_user_ctrl.get_employees_from_team.return_value = [
                MagicMock(id=10, name="Commercial 1")
            ]
            mock_user_ctrl.view = MagicMock()
            mock_user_ctrl.view.choose_support_collab = MagicMock(return_value=None)
            mock_user_ctrl_cls.return_value = mock_user_ctrl

            client_controller.add_sales_rep_collab_to_client()

            # Vérifier que le commercial n'a pas été affecté au client
            assert fake_clients[0].commercial_id is None

            mock_user_ctrl.view.choose_support_collab.assert_called_once()
