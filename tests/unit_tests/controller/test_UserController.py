import pytest
from unittest.mock import MagicMock, patch

from models import User, Team
from controller.RegisterController import UserController

@pytest.fixture
def user_controller():
    mock_session = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.obj = {
        "session": mock_session,
        "SECRET_KEY": "fake_secret_key"
    }
    controller = UserController(ctx=mock_ctx)
    controller.view = MagicMock()
    controller.session = mock_session
    return controller

class TestUserController:

    def test_create_co_worker_success(self,user_controller):

        mock_team = MagicMock()
        mock_team.id = 1
        user_controller.session.query().filter_by().first.return_value = mock_team

        with patch.object(user_controller,"_UserController__hash_passwords",return_value="hashed_pwd"), \
            patch.object(user_controller,"email_exists_in_db", return_value=False), \
            patch.object(user_controller,"validate_user_data", return_value=[]), \
            patch("controller.UserController.commit_to_db") as mock_commit:
            user_controller.create_co_worker("test@email.com","first","last","phone","team")

        user_controller.view.success_message.assert_called_with("first","last")
        mock_commit.assert_called_once()
        user_controller.view.message_adding_co_worker_failed.assert_not_called()
        user_controller.view.message_email_exists.assert_not_called()

    def test_create_co_worker_existent_email(self,user_controller):

        mock_team = MagicMock()
        mock_team.id = 1
        user_controller.session.query().filter_by().first.return_value = mock_team

        with patch.object(user_controller,"_UserController__hash_passwords",return_value="hashed_pwd"), \
            patch.object(user_controller,"email_exists_in_db", return_value=True), \
            patch("controller.UserController.commit_to_db") as mock_commit:
            user_controller.create_co_worker("test@email.com","first","last","phone","team")

        user_controller.view.success_message.assert_not_called()
        mock_commit.assert_not_called()
        user_controller.view.message_adding_co_worker_failed.assert_not_called()
        user_controller.view.message_email_exists.assert_called_once()

    def test_create_co_worker_data_error(self,user_controller):

        mock_team = MagicMock()
        mock_team.id = 1
        user_controller.session.query().filter_by().first.return_value = mock_team

        with patch.object(user_controller,"_UserController__hash_passwords",return_value="hashed_pwd"), \
            patch.object(user_controller,"email_exists_in_db", return_value=False), \
            patch.object(user_controller,"validate_user_data", return_value=["errors"]), \
            patch("controller.UserController.commit_to_db") as mock_commit:
            user_controller.create_co_worker("test@email.com","first","last","phone","team")

        user_controller.view.success_message.assert_not_called()
        mock_commit.assert_not_called()
        user_controller.view.message_adding_co_worker_failed.assert_called()
        user_controller.view.message_email_exists.assert_not_called()

    def test_update_co_worker_success(self, user_controller):
        fake_user = MagicMock()
        fake_user.first_name = "First"
        fake_user.last_name = "Last"
        fake_user.email_address = "test@email.com"
        fake_user.phone = "0102030405"
        fake_team = MagicMock()
        fake_user.team = fake_team

        with patch.object(user_controller, "select_co_worker", return_value=fake_user), \
            patch.object(user_controller.view, "get_co_worker_new_data", return_value=fake_user), \
            patch.object(user_controller, "validate_user_data", return_value=[]), \
            patch("controller.UserController.commit_to_db") as mock_commit:

            user_controller.update_co_worker()
        mock_commit.assert_called_once()

    def test_update_co_worker_invalid_data(self, user_controller):
        fake_user = MagicMock()
        fake_user.first_name = "First"
        fake_user.last_name = "Last"
        fake_user.email_address = "test@email.com"
        fake_user.phone = "0102030405"
        fake_team = MagicMock()
        fake_user.team = fake_team

        errors = ["invalid email"]

        with patch.object(user_controller, "select_co_worker",
                          return_value=fake_user), \
                patch.object(user_controller.view,
                             "get_co_worker_new_data", return_value=fake_user), \
                patch.object(user_controller, "validate_user_data",
                             return_value=errors), \
                patch.object(user_controller.view,
                             "message_updating_co_worker_failed") as mock_message, \
                patch(
                    "controller.UserController.commit_to_db") as mock_commit:
            user_controller.update_co_worker()

        mock_message.assert_called_once_with(errors)
        mock_commit.assert_not_called()

    def test_update_co_worker_related_data_commercial(self, user_controller):
        co_worker = MagicMock()
        co_worker.id = 1
        co_worker.team = "Commercial"

        fake_clients = [MagicMock(commercial_id=1), MagicMock(commercial_id=1)]
        fake_contracts = [MagicMock(commercial_id=1)]

        user_controller.session.query().filter().all.side_effect = [fake_clients,
                                                         fake_contracts]

        user_controller.update_co_worker_related_data(co_worker)

        for client in fake_clients:
            assert client.commercial_id is None
        for contract in fake_contracts:
            assert contract.commercial_id is None

    def test_update_co_worker_related_data_support(self,user_controller):
        co_worker = MagicMock()
        co_worker.id = 2
        co_worker.team = "Support"

        fake_events = [MagicMock(support_id=2), MagicMock(support_id=2)]

        user_controller.session.query().filter().all.return_value = fake_events

        user_controller.update_co_worker_related_data(co_worker)

        for event in fake_events:
            assert event.support_id is None

    def test_update_co_worker_related_data_gestion(self,user_controller):
        co_worker = MagicMock()
        co_worker.team = "Gestion"

        user_controller.update_co_worker_related_data(co_worker)

    def test_delete_co_worker_success(self, user_controller):
        co_worker = MagicMock()
        co_worker.id = 1
        co_worker.first_name = "First"
        co_worker.last_name = "Last"
        co_worker.team = "Commercial"

        user_controller.select_co_worker = MagicMock(return_value=co_worker)
        user_controller.update_co_worker_related_data = MagicMock()
        user_controller.session.query().filter().first.return_value = None

        with patch("controller.UserController.commit_to_db") as mock_commit, \
                patch("controller.UserController.logger") as mock_logger:
            user_controller.delete_co_worker()

        user_controller.update_co_worker_related_data.assert_called_once_with(
            co_worker)
        user_controller.session.delete.assert_called_once_with(co_worker)
        mock_commit.assert_called_once_with(user_controller.session, user_controller.view)
        user_controller.view.message_co_worker_deleted.assert_called_once()
        mock_logger.info.assert_called_once_with(
            f"User {co_worker.first_name} {co_worker.last_name} has been deleted!")

    def test_delete_co_worker_none_selected(self, user_controller):
        user_controller.select_co_worker = MagicMock(return_value=None)
        user_controller.update_co_worker_related_data = MagicMock()

        user_controller.delete_co_worker()

        user_controller.update_co_worker_related_data.assert_not_called()
        user_controller.session.delete.assert_not_called()

    def test_get_my_clients(self, user_controller):
        fake_user = MagicMock()
        fake_user.id = 1

        fake_clients = [MagicMock(name="Client1"), MagicMock(name="Client2")]

        user_controller.session.query().filter().all.return_value = fake_clients

        with patch(
                "controller.UserController.TokenManagement.get_connected_user",
                return_value=fake_user):

            result = user_controller.get_my_clients()

        assert result == fake_clients
        user_controller.view.show_my_clients.assert_called_once_with(
            fake_clients)

    def test_select_co_worker_3(self, user_controller):
        fake_co_workers = [MagicMock(id=1, first_name="Alice"),
                           MagicMock(id=2, first_name="Bob")]
        fake_user = fake_co_workers[0]  # l'utilisateur qui sera retourné

        user_controller.session.query().filter().first.return_value = fake_user

        with patch.object(user_controller, "display_co_workers", return_value=fake_co_workers) as mock_show, \
                patch("controller.UserController.get_ids", return_value=[1,2]), \
                patch.object(user_controller.view, "get_co_worker", return_value=1) as mock_get:
            result = user_controller.select_co_worker("update")

        assert result == fake_user
        mock_show.assert_called_once()
        mock_get.assert_called_once_with([1, 2],"update")
