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
                "Are you confirming your disconnection ? (y/n) : ").strip().lower()
            if choice not in ("y", "n"):
                print("Please input 'y' for yes or 'n' for no.")

        return choice == 'y'

    @staticmethod
    def print_logged_out_message():
        click.echo("You are disconnected.")

    @staticmethod
    def print_staying_logged_message():
        click.echo("Back to menu.")

    @staticmethod
    def print_exit_message():
        click.echo("End of the program. 'python main.py' to start again.")


