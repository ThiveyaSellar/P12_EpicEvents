from unittest.mock import MagicMock, patch

import pytest
from controller.MenuController import MenuController

@pytest.fixture
def menu_controller():
    controller = MenuController()
    controller.view = MagicMock()
    return controller

class TestMenuController:

    # Mocker exit pour éviter que le test s'arrête
    @patch("builtins.exit")
    def test_create_login_menu_exit(self, mock_exit, menu_controller):
        menu_controller.view.show_login_menu.return_value = 'exit'
        mock_cli = MagicMock()
        menu_controller.create_login_menu(mock_cli)
        mock_exit.assert_called_once()

    def test_create_login_menu_cmd_calls_cli_main(self, menu_controller):
        menu_controller.view.show_login_menu.return_value = 'login'
        mock_cli = MagicMock()
        menu_controller.create_login_menu(mock_cli)
        mock_cli.main.assert_called_once_with(['login'], standalone_mode=False)

    def test_show_team_menu_sales_menu(self, menu_controller):
        team = "Commercial"
        menu_controller.show_team_menu(team)
        assert menu_controller.view.show_sales_menu.called
        assert not menu_controller.view.show_management_menu.called
        assert not menu_controller.view.show_support_menu.called

    def test_show_team_menu_management_menu(self, menu_controller):
        team = "Gestion"
        menu_controller.show_team_menu(team)
        assert not menu_controller.view.show_sales_menu.called
        assert menu_controller.view.show_management_menu.called
        assert not menu_controller.view.show_support_menu.called

    def test_show_team_menu_support_menu(self, menu_controller):
        team = "Support"
        menu_controller.show_team_menu(team)
        assert not menu_controller.view.show_sales_menu.called
        assert not menu_controller.view.show_management_menu.called
        assert menu_controller.view.show_support_menu.called

    def test_show_team_menu_incorrect_team(self, menu_controller):
        team = "Incorrect"
        menu_controller.show_team_menu(team)
        assert not menu_controller.view.show_sales_menu.called
        assert not menu_controller.view.show_management_menu.called
        assert not menu_controller.view.show_support_menu.called
        assert menu_controller.view.show_team_error.called

    def test_logout(self, menu_controller):
        menu_controller.logout()
        assert menu_controller.view.logout_message.called

    def test_create_main_menu_user_none(self, menu_controller):
        user = None
        mock_cli = MagicMock()
        mock_session = MagicMock()
        mock_SECRET_KEY = MagicMock()

        menu_controller.view.ask_cmd_input = MagicMock(side_effect=KeyboardInterrupt())
        try:
            menu_controller.create_main_menu(user,mock_cli,mock_session,mock_SECRET_KEY)
        except KeyboardInterrupt:
            pass
        assert menu_controller.view.msg_user_none.called

    def test_create_main_menu_not_connected(self, menu_controller):
        user = MagicMock()
        user.team.name = "Support"

        mock_cli = MagicMock()
        mock_session = MagicMock()
        SECRET_KEY = "test"

        with patch("controller.MenuController.TokenManagement.checking_user_connection") as mock_check_user_connection, patch("builtins.exit") as mock_exit:

            # No user, not connected
            mock_check_user_connection.return_value = (False, None)

            menu_controller.view.print_connection_error = MagicMock()

            menu_controller.view.ask_cmd_input = MagicMock()

            menu_controller.create_main_menu(user, mock_cli, mock_session,
                                             SECRET_KEY)

            menu_controller.view.print_connection_error.assert_called_once()
            mock_exit.assert_called_once()

    def test_create_main_menu_no_command(self, menu_controller):
        user = MagicMock()
        user.team.name = "Support"

        mock_cli = MagicMock()
        mock_session = MagicMock()
        SECRET_KEY = "test"

        with patch("controller.MenuController.TokenManagement.checking_user_connection") as mock_check_user_connection:

            # User, connected
            mock_check_user_connection.return_value = (True, user)

            menu_controller.view.ask_cmd_input = MagicMock(side_effect=["", KeyboardInterrupt()])
            try:
                menu_controller.create_main_menu(user, mock_cli, mock_session,
                                             SECRET_KEY)
            except KeyboardInterrupt:
                pass
            menu_controller.view.message_input_command.assert_called_once()

    def test_create_main_menu_login_command(self, menu_controller):
        user = MagicMock()
        user.team.name = "Support"

        mock_cli = MagicMock()
        mock_session = MagicMock()
        SECRET_KEY = "test"

        with patch("controller.MenuController.TokenManagement.checking_user_connection") as mock_check_user_connection:

            # User, connected
            mock_check_user_connection.return_value = (True, user)

            menu_controller.view.ask_cmd_input = MagicMock(side_effect=["login", KeyboardInterrupt()])
            try:
                menu_controller.create_main_menu(user, mock_cli, mock_session,
                                             SECRET_KEY)
            except KeyboardInterrupt:
                pass
            menu_controller.view.message_already_connected.assert_called_once()

    def test_create_main_menu_authorized_command(self, menu_controller):
        user = MagicMock()
        user.team.name = "Support"

        mock_cli = MagicMock()
        mock_session = MagicMock()
        SECRET_KEY = "test"

        with patch("controller.MenuController.TokenManagement.checking_user_connection") as mock_check_user_connection, \
            patch("controller.MenuController.is_authorized") as mock_auth, \
            patch("controller.MenuController.command_exists") as mock_command_exists:

            # User, connected
            mock_check_user_connection.return_value = (True, user)
            mock_auth.return_value = True
            mock_command_exists.return_value = True

            menu_controller.view.ask_cmd_input = MagicMock(side_effect=["update-my-event", KeyboardInterrupt()])

            try:
                menu_controller.create_main_menu(user, mock_cli, mock_session,
                                             SECRET_KEY)
            except KeyboardInterrupt:
                pass
            mock_cli.main.assert_called_once_with(['update-my-event'], standalone_mode=False)

    def test_create_main_menu_unauthorized_command(self, menu_controller):
        user = MagicMock()
        user.team.name = "Support"

        mock_cli = MagicMock()
        mock_session = MagicMock()
        SECRET_KEY = "test"

        with patch("controller.MenuController.TokenManagement.checking_user_connection") as mock_check_user_connection, \
            patch("controller.MenuController.is_authorized") as mock_auth, \
            patch("controller.MenuController.command_exists") as mock_command_exists:

            # User, connected
            mock_check_user_connection.return_value = (True, user)
            mock_auth.return_value = False
            mock_command_exists.return_value = True

            menu_controller.view.ask_cmd_input = MagicMock(side_effect=["create-my-client", KeyboardInterrupt()])

            try:
                menu_controller.create_main_menu(user, mock_cli, mock_session,
                                             SECRET_KEY)
            except KeyboardInterrupt:
                pass
            menu_controller.view.message_unauthorized_cmd.assert_called_once_with(user.team.name)