import sys, click

from controller.LoginController import LoginController
from controller.RegisterController import RegisterController
from utils.validators import validate_email_callback, validate_name, \
    validate_phone_callback


def register_auth_commands(cli):
    @cli.command()
    @click.pass_context
    @click.option("--email", prompt="Email", callback=validate_email_callback,
                  help="Votre email")
    @click.option("--password", prompt="Mot de passe", hide_input=True,
                  help="Votre mot de passe")
    def login(ctx, email, password):
        controller = LoginController(ctx)
        controller.login(email, password)

    @cli.command()
    @click.pass_context
    @click.option("--email", prompt="Email", callback=validate_email_callback,
                  help="Votre email")
    @click.option("--password", prompt="Mot de passe", hide_input=True,
                  help="Votre mot de passe")
    @click.option("--password2", prompt="Confirmation de mot de passe",
                  hide_input=True,
                  help="Votre mot de passe")
    @click.option("--first_name", prompt="Prénom", callback=validate_name,
                  help="Votre prénom")
    @click.option("--last_name", prompt="Nom", callback=validate_name,
                  help="Votre nom")
    @click.option("--phone", prompt="Numéro de téléphone",
                  callback=validate_phone_callback, help="Votre téléphone")
    @click.option("--team",
                  type=click.Choice(["Commercial", "Gestion", "Support"],
                                    case_sensitive=False),
                  prompt="Équipe", help="Votre équipe")
    def register(ctx, email, password, password2, first_name, last_name, phone,
                 team):
        controller = RegisterController(ctx)
        controller.register(email, password, password2, first_name, last_name,
                            phone, team)

    @cli.command()
    @click.pass_context
    def logout(ctx):
        controller = LoginController(ctx)
        controller.logout()

    @cli.command()
    @click.pass_context
    def exit(ctx):
        controller = LoginController(ctx)
        controller.exit_program()
        sys.exit()