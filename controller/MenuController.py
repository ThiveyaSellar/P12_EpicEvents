from views.MenuView import MenuView

class MenuController:

    def __init__(self):
        self.view = MenuView()

    def create_login_menu(self, cli):
        cmd = self.view.show_login_menu()
        if cmd == 'exit':
            exit()
        cli.main(cmd.split(), standalone_mode=False)

    def create_main_menu(self, user, cli):

        # Permissions par équipe
        all_permissions = [
            "show_clients",
            "show_contracts",
            "show_events",
            "logout"
        ]

        sales_permissions = all_permissions + \
                            [
                                "create_client",
                                "update_client",
                                "show_specific_contracts",
                                "update_my_contracts",
                                "create_event_for_my_client"
                            ]

        support_permissions = all_permissions + \
                              [
                                  "update_support_event",
                                  "show_support_events"
                              ]
        
        management_permissions = all_permissions + [""]

        permissions = {
            "Commercial": sales_permissions,
            "Support": support_permissions,
            "Gestion": management_permissions
        }

        while True:
            try:
                if user is None:
                    self.view.msg_user_none()
                team = user.team.name
                if team == "Commercial":
                    self.view.show_sales_menu()
                elif team == "Gestion":
                    pass
                elif team == "Support":
                    self.view.show_support_menu()
                # Print menu and get command from user input
                # self.view.show_main_menu(user, team)
                cmd = self.view.ask_cmd_input()
                # Vérifie que la commande est autorisée
                cmd_parts = cmd.split()
                main_cmd = cmd_parts[0] if cmd_parts else ""

                if main_cmd in permissions.get(team, []):
                    cli.main(cmd_parts, standalone_mode=False)
                else:
                    self.view.print_error_message(
                        f"Commande non autorisée pour l’équipe {team}")
            except Exception as e:
                self.view.print_error_message(e)
                break