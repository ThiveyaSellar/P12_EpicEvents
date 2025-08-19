import click

class RegisterView:

    @staticmethod
    def print_password_error():
        click.echo(f"Les mots de passe ne matchent pas.")

    @staticmethod
    def success_message(first_name, last_name):
        click.echo(f"Inscription réussie pour {first_name} {last_name}.")

    @staticmethod
    def message_email_exists():
        click.echo("Cet email est déjà utilisé.")

    @staticmethod
    def message_registration_failed(errors):
        click.echo("Registration has failed.")
        click.echo(errors)