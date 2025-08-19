import os, sys, click
# Ajouter le répertoire racine au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from utils.TokenManagement import TokenManagement


from controller.MenuController import MenuController


from commands.support import register_support_commands
from commands.sales_rep import register_sales_rep_commands
from commands.management import register_management_commands
from commands.common import register_common_commands
from commands.auth import register_auth_commands

from settings import Settings

settings = Settings()
session = settings.session
SECRET_KEY = settings.secret_key

@click.group()
@click.pass_context
def cli(ctx):
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj["session"] = session
    ctx.obj["SECRET_KEY"] = SECRET_KEY

register_auth_commands(cli)
register_support_commands(cli)
register_management_commands(cli)
register_sales_rep_commands(cli)
register_common_commands(cli)

def main():
    menu_controller = MenuController()
    # Vérifier qu'il y a un token permettant d'identifier l'utilisateur et s'il est valide
    connected, user = TokenManagement.checking_user_connection(session,
                                                               SECRET_KEY)
    while not connected:
        # Menu avec soit inscription soit connexion
        # Execution des commandes login et register
        menu_controller.create_login_menu(cli)
        # Vérification de l'execution de login

        # Vérifier si l'utilisateur est connecté (s'il s'est loggé)
        connected, user = TokenManagement.checking_user_connection(session,
                                                                   SECRET_KEY)

    menu_controller.create_main_menu(user, cli, session, SECRET_KEY)

if __name__ == "__main__":
    main()
