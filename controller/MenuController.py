from views.MenuView import MenuView
from utils.permissions import is_authorized, PERMISSIONS
from utils.TokenManagement import TokenManagement


class MenuController:

    def __init__(self):
        self.view = MenuView()

    def create_login_menu(self, cli):
        cmd = self.view.show_login_menu()
        if cmd == 'exit':
            exit()
        cli.main(cmd.split(), standalone_mode=False)

    def create_main_menu(self, user, cli, session, SECRET_KEY):
        while True:
            try:
                if user is None:
                    self.view.msg_user_none()
                team = user.team.name
                if team == "Commercial":
                    self.view.show_sales_menu()
                elif team == "Gestion":
                    self.view.show_management_menu()
                elif team == "Support":
                    self.view.show_support_menu()

                # Vérifier si l'utilisateur est toujours connecté
                connected, user = TokenManagement.checking_user_connection(
                    session,
                    SECRET_KEY
                )
                if not connected:
                    print("Veuillez vous reconnecter.")
                    exit()
                # Print menu and get command from user input
                # self.view.show_main_menu(user, team)
                cmd = self.view.ask_cmd_input()
                # Vérifie que la commande est autorisée
                cmd_parts = cmd.split()
                command = cmd_parts[0] if cmd_parts else ""

                if is_authorized(team, command, PERMISSIONS):
                    cli.main(cmd_parts, standalone_mode=False)
                elif command == "":
                    print("Veuillez saisir une commande.")
                else:
                    self.view.print_error_message(
                        f"Commande non autorisée pour l’équipe {team}")
            except Exception as e:
                self.view.print_error_message(e)
                break

    def logout(self):
        self.view.logout_message()