from unittest.mock import MagicMock, patch, ANY

import pytest
from controller.LoginController import LoginController
from sqlalchemy.orm.exc import NoResultFound
from models import User

@pytest.fixture
def login_controller():
    mock_session = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.obj = {
        "session": mock_session,
        "SECRET_KEY": "fake_secret_key"
    }
    controller = LoginController(ctx=mock_ctx)
    controller.view = MagicMock()
    controller.session = mock_session

    return controller

class TestLoginController:

    def test_check_user_mail_success(self, login_controller):
        controller = login_controller
        fake_user = MagicMock()
        fake_user.email_address = 'test@epicevents.com'
        query_mock = controller.session.query.return_value
        filter_mock = query_mock.filter_by.return_value
        filter_mock.one.return_value = fake_user

        result = controller.check_user_mail('test@epicevents.com')

        controller.session.query.assert_called_once_with(User)
        query_mock.filter_by.assert_called_once_with(email_address='test@epicevents.com')
        assert result == fake_user

    def test_check_user_mail_not_found(self, login_controller):
        controller = login_controller

        query_mock = controller.session.query.return_value
        filter_mock = query_mock.filter_by.return_value
        filter_mock.one.side_effect = Exception('No result found')

        with pytest.raises(Exception) as exp:
            controller.check_user_mail("inexistent@epicevents.com")

        assert 'No result found' in str(exp.value)

    def test_login_user_not_found(self, login_controller):
        controller = login_controller
        controller.check_user_mail = MagicMock(side_effect=NoResultFound)
        controller.view.print_user_not_found = MagicMock()

        result = controller.login("inexistent@epicevents.com","pwd")

        controller.view.print_user_not_found.assert_called_once()
        assert result is None

    def test_login_bad_password(self, login_controller):
        controller = login_controller
        fake_user = MagicMock()
        fake_user.password = 'test'
        controller.check_user_mail = MagicMock(return_value=fake_user)
        controller.verify_password = MagicMock(return_value=False)
        controller.view.print_password_error = MagicMock()

        result = controller.login("test@epicevents.com","incorrect")

        controller.view.print_password_error.assert_called_once()
        assert result is None

    def test_login_success(self, login_controller):
        controller = login_controller
        fake_user = MagicMock(password="hashed-pwd")
        controller.check_user_mail = MagicMock(return_value=fake_user)
        controller.verify_password = MagicMock(return_value=True)
        controller.define_token = MagicMock(side_effect=["access","token"])
        controller.write_in_netrc = MagicMock()

        with patch("controller.LoginController.commit_to_db") as mock_commit:
            controller.login("user@epicevents.com", "good-pwd")

        controller.define_token.assert_any_call(ANY, "fake_secret_key", 1)
        controller.define_token.assert_any_call(ANY, "fake_secret_key", 3)

        controller.write_in_netrc.assert_called_once_with("access", "token")

        controller.view.print_welcome_message.assert_called_once_with(fake_user)

    def test_logout_confirmed(self, login_controller):
        login_controller.view.get_logout_confirmation.return_value = True

        with patch("controller.LoginController.TokenManagement.get_netrc_path",
                   return_value="fake_path") as mock_path, \
                patch(
                    "controller.LoginController.TokenManagement.update_tokens_in_netrc") as mock_update, \
                patch("controller.LoginController.exit") as mock_exit:
            login_controller.logout()

            mock_path.assert_called_once()
            mock_update.assert_called_once_with("127.0.0.1", "", "",
                                                "fake_path")
            login_controller.view.print_logged_out_message.assert_called_once()
            mock_exit.assert_called_once()

    def test_logout_cancelled(self, login_controller):
        login_controller.view.get_logout_confirmation.return_value = False

        with patch(
                "controller.LoginController.TokenManagement.update_tokens_in_netrc") as mock_update, \
                patch("controller.LoginController.exit") as mock_exit:
            login_controller.logout()

        login_controller.view.print_staying_logged_message.assert_called_once()
        mock_update.assert_not_called()
        mock_exit.assert_not_called()

    def test_exit_program(self, login_controller):
        login_controller.exit_program()
        login_controller.view.print_exit_message.assert_called()

    def test_change_password_user_not_connected(self, login_controller):

        with patch("controller.LoginController.TokenManagement.checking_user_connection",
                   return_value=(False,None)) as mock_check_conn:
            result = login_controller.change_password()

            mock_check_conn.assert_called_once_with(login_controller.session,
                                                    login_controller.SECRET_KEY)

            assert result is None
            login_controller.view.confirm_update_and_login.assert_not_called()

    def test_change_password_success(self, login_controller):
        fake_user = MagicMock()
        fake_user.email_address = "test@test.com"
        fake_user.password = "hashed_password"

        with patch("controller.LoginController.TokenManagement.checking_user_connection", return_value=(True,fake_user)), \
            patch("controller.LoginController.LoginView.ask_old_password", return_value="correct_pwd"), \
            patch.object(login_controller, "verify_password", return_value=True), \
            patch("controller.LoginController.LoginView.get_new_passwords",return_value=("new_pwd","new_pwd")), \
            patch.object(login_controller,"_LoginController__hash_passwords", return_value="hashed_new_pwd"), \
            patch("controller.LoginController.commit_to_db") as mock_commit, \
            patch("controller.LoginController.TokenManagement.get_netrc_path", return_value="/tmp/netrc"), \
            patch("controller.LoginController.TokenManagement.update_tokens_in_netrc") as mock_update, \
            patch("controller.LoginController.exit") as mock_exit:

            login_controller.change_password()

        login_controller.view.confirm_update_and_login.assert_called()
        mock_exit.assert_called_once()
        assert fake_user.password == "hashed_new_pwd"
        mock_commit.assert_called_once()
        mock_update.assert_called_once_with("127.0.0.1", "", "", "/tmp/netrc")
        login_controller.view.confirm_update_and_login.assert_called_once()
        mock_exit.assert_called_once()

    def test_change_password_wrong_old_password(self, login_controller):
        fake_user = MagicMock()
        fake_user.email_address = "test@test.com"
        fake_user.password = "hashed_password"

        with patch("controller.LoginController.TokenManagement.checking_user_connection", return_value=(True,fake_user)), \
            patch("controller.LoginController.LoginView.ask_old_password", return_value="wrong_pwd"), \
            patch("controller.LoginController.LoginView.ask_old_pwd_again", return_value="correct_pwd"), \
            patch.object(login_controller, "verify_password", side_effect=[False,True]), \
            patch("controller.LoginController.LoginView.get_new_passwords",return_value=("new_pwd","new_pwd")), \
            patch.object(login_controller,"_LoginController__hash_passwords", return_value="hashed_new_pwd"), \
            patch("controller.LoginController.commit_to_db") as mock_commit, \
            patch("controller.LoginController.TokenManagement.get_netrc_path", return_value="/tmp/netrc"), \
            patch("controller.LoginController.TokenManagement.update_tokens_in_netrc") as mock_update, \
            patch("controller.LoginController.exit") as mock_exit:

            login_controller.change_password()

            login_controller.view.confirm_update_and_login.assert_called()
            mock_exit.assert_called_once()
            assert fake_user.password == "hashed_new_pwd"
            mock_commit.assert_called_once()
            mock_update.assert_called_once_with("127.0.0.1", "", "",
                                                "/tmp/netrc")


    def test_change_password_ask_new_password_again(self, login_controller):
        fake_user = MagicMock()
        fake_user.email_address = "test@test.com"
        fake_user.password = "hashed_password"

        with patch("controller.LoginController.TokenManagement.checking_user_connection", return_value=(True,fake_user)), \
            patch("controller.LoginController.LoginView.ask_old_password", return_value="correct_pwd"), \
            patch.object(login_controller, "verify_password", return_value=True), \
            patch("controller.LoginController.LoginView.get_new_passwords",return_value=("new_pwd","new_wrong_pwd")), \
            patch("controller.LoginController.LoginView.ask_new_passwords_again", side_effect=[("new_pwd","new_pwd")]), \
            patch.object(login_controller,"_LoginController__hash_passwords", return_value="hashed_new_pwd"), \
            patch("controller.LoginController.commit_to_db") as mock_commit, \
            patch("controller.LoginController.TokenManagement.get_netrc_path", return_value="/tmp/netrc"), \
            patch("controller.LoginController.TokenManagement.update_tokens_in_netrc") as mock_update, \
            patch("controller.LoginController.exit") as mock_exit:

            login_controller.change_password()

            login_controller.view.confirm_update_and_login.assert_called()
            mock_exit.assert_called_once()
            assert fake_user.password == "hashed_new_pwd"
            mock_commit.assert_called_once()
            mock_update.assert_called_once_with("127.0.0.1", "", "",
                                                "/tmp/netrc")


