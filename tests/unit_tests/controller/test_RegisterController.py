import pytest
from unittest.mock import MagicMock, patch

from controller.RegisterController import RegisterController

@pytest.fixture
def register_controller():
    mock_session = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.obj = {
        "session": mock_session,
        "SECRET_KEY": "fake_secret_key"
    }
    controller = RegisterController(ctx=mock_ctx)
    controller.view = MagicMock()
    controller.session = mock_session
    return controller

class TestRegisterController:

    def test_register_success(self, register_controller):
        mock_team = MagicMock()
        mock_team.id = 1

        register_controller.session.query().filter_by().first.return_value = mock_team

        with patch.object(register_controller,"email_exists_in_db", return_value=False), \
        patch("controller.RegisterController.validate_password", return_value=True), \
        patch.object(register_controller, "_RegisterController__hash_passwords", return_value="hashed_password"), \
        patch.object(register_controller,"validate_user_data", return_value=[]), \
        patch("controller.RegisterController.commit_to_db") as mock_commit:
            register_controller.register("test@test.com","pwd","pwd","name","name","0102030405",mock_team)

        register_controller.view.success_message.assert_called_once_with("name","name")
        register_controller.view.message_email_exists.assert_not_called()
        register_controller.view.print_password_error.assert_not_called()
        register_controller.view.message_registration_failed.assert_not_called()
        mock_commit.assert_called_once()

    def test_register_existent_email(self, register_controller):

        with patch.object(register_controller,"email_exists_in_db", return_value=True), \
        patch("controller.RegisterController.commit_to_db") as mock_commit:
            register_controller.register("test@test.com","pwd","pwd","name","name","0102030405","Team A")

        register_controller.view.success_message.assert_not_called()
        register_controller.view.message_email_exists.assert_called_once()
        register_controller.view.print_password_error.assert_not_called()
        mock_commit.assert_not_called()

    def test_register_invalid_passwords(self,register_controller):
        with patch.object(register_controller, "email_exists_in_db",
                          return_value=False), \
                patch("controller.RegisterController.validate_password",
                      return_value=False), \
                patch(
                    "controller.RegisterController.commit_to_db") as mock_commit:
            register_controller.register("test@test.com", "pwd", "pwd", "name",
                                         "name", "0102030405", "Team A")

        register_controller.view.success_message.assert_not_called()
        register_controller.view.message_email_exists.assert_not_called()
        register_controller.view.print_password_error.assert_called_once()
        mock_commit.assert_not_called()

    def test_register_with_errors(self, register_controller):
        mock_team = MagicMock()
        mock_team.id = 1

        register_controller.session.query().filter_by().first.return_value = mock_team

        with patch.object(register_controller, "email_exists_in_db",
                          return_value=False), \
                patch("controller.RegisterController.validate_password",
                      return_value=True), \
                patch.object(register_controller,
                             "_RegisterController__hash_passwords",
                             return_value="hashed_password"), \
                patch.object(register_controller, "validate_user_data",
                             return_value=["errors"]), \
                patch(
                    "controller.RegisterController.commit_to_db") as mock_commit:
            register_controller.register("test@test.com", "pwd", "pwd", "name",
                                         "name", "0102030405", mock_team)

        register_controller.view.success_message.assert_not_called()
        register_controller.view.message_email_exists.assert_not_called()
        register_controller.view.print_password_error.assert_not_called()
        register_controller.view.message_registration_failed.assert_called()
        mock_commit.assert_not_called()

    def test_validate_user_data_correct(self, register_controller):
        data = {
            "email": "test@email.com",
            "first_name": "first",
            "last_name": "last",
            "phone": "0102030405",
            "team": "Commercial"
        }
        with patch("controller.RegisterController.check_email_field"), \
                patch("controller.RegisterController.check_field_and_length"), \
                patch("controller.RegisterController.check_phone_field"), \
                patch("controller.RegisterController.check_team_field"):
            errors = register_controller.validate_user_data(data)

        assert errors == []

    def test_validate_user_data_incorrect(self, register_controller):
        data = {
            "email": "testemail.com",
            "first_name": "first",
            "last_name": "last",
            "phone": "0102030405",
            "team": "Commercial"
        }

        errors = register_controller.validate_user_data(data)

        assert errors != []
        assert "Email is not valid or too long." in errors


