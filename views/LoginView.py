import click


class LoginView:

    @staticmethod
    def print_password_error():
        click.echo("Password is incorrect.")

    @staticmethod
    def print_welcome_message(user):
        message = (
            "--------------------------------------\n"
            "Successful connection.\n"
            f"Welcome {user.first_name} {user.last_name}!"
        )
        click.echo(message)

    @staticmethod
    def print_user_not_found():
        click.echo("User is not found.")

    @staticmethod
    def get_logout_confirmation():
        choice = ""
        while choice not in ("y", "n"):
            choice = input(
                "Are you confirming your disconnection ? (y/n) : "
            ).strip().lower()
            if choice not in ("y", "n"):
                print("Please input 'y' for yes or 'n' for no.")

        return choice == 'y'

    @staticmethod
    def print_logged_out_message():
        click.echo("You are disconnected.")

    @staticmethod
    def confirm_update_and_login():
        click.echo("Password is updated, please login again.")

    @staticmethod
    def print_staying_logged_message():
        click.echo("Back to menu.")

    @staticmethod
    def print_exit_message():
        click.echo("End of the program. 'python main.py' to start again.")

    @staticmethod
    def message_db_error(errors):
        # Affiche proprement même si errors est une liste ou autre
        if isinstance(errors, list):
            for e in errors:
                click.echo(str(e))
        else:
            click.echo(str(errors))

    @staticmethod
    def ask_old_password(email):
        click.echo(f"Email: {email}")
        return click.prompt("Old password", hide_input=True)

    @staticmethod
    def get_new_passwords():
        new_password = click.prompt("New password", hide_input=True)
        new_password_2 = click.prompt(
            "Confirm your new password",
            hide_input=True
        )
        return new_password, new_password_2

    @staticmethod
    def ask_old_pwd_again():
        click.echo("Wrong password, try again!")
        return click.prompt("Old password", hide_input=True)

    @staticmethod
    def ask_new_passwords_again():
        click.echo("Passwords don't match, please try again.")
        new_password = click.prompt("New password", hide_input=True)
        new_password_2 = click.prompt(
            "Confirm your new password",
            hide_input=True
        )
        return new_password, new_password_2
