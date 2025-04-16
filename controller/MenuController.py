import click
from views.MenuView import MenuView

from controller.LoginController import LoginView


class MenuController:

    def __init__(self):
        self.view = MenuView()

    def create_login_menu(self, cli):
        cmd = self.view.show_login_menu()
        if cmd == 'exit':
            exit()
        cli.main(cmd.split(), standalone_mode=False)

    def create_main_menu(self, user, cli):
        while True:
            try:
                if user is None:
                    self.view.msg_user_none()
                team = user.team.name
                # Print menu and get command from user input
                self.view.show_main_menu(user, team)
                cmd = self.view.ask_cmd_input()
                if cmd.lower() in ["exit", "quit"]:
                    break
                cli.main(cmd.split(), standalone_mode=False)
            except Exception as e:
                self.view.print_error_message(e)
                break