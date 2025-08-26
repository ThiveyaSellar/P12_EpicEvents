import sys, click

from controller.LoginController import LoginController
from controller.RegisterController import RegisterController
from controller.UserController import UserController
from utils.validators import validate_email_callback, validate_name, \
    validate_phone_callback


def register_auth_commands(cli):
    @cli.command()
    @click.pass_context
    @click.option("--email", prompt="Email", callback=validate_email_callback,
                  help="Your email")
    @click.option("--password", prompt="Password", hide_input=True,
                  help="Your password")
    def login(ctx, email, password):
        controller = LoginController(ctx)
        controller.login(email, password)

    @cli.command()
    @click.pass_context
    @click.option("--email", prompt="Email", callback=validate_email_callback,
                  help="Your email")
    @click.option("--password", prompt="Password", hide_input=True,
                  help="Your password")
    @click.option("--password2", prompt="Confirm your password",
                  hide_input=True,
                  help="Your password")
    @click.option("--first_name", prompt="First name", callback=validate_name,
                  help="Your first name")
    @click.option("--last_name", prompt="Last name", callback=validate_name,
                  help="Your last name")
    @click.option("--phone", prompt="Phone number",
                  callback=validate_phone_callback, help="Your phone number")
    @click.option("--team",
                  type=click.Choice(["Commercial", "Gestion", "Support"],
                                    case_sensitive=False),
                  prompt="Team", help="Your team")
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
    def change_password(ctx):
        controller = LoginController(ctx)
        controller.change_password()

    @cli.command()
    @click.pass_context
    def exit(ctx):
        controller = LoginController(ctx)
        controller.exit_program()
        sys.exit()