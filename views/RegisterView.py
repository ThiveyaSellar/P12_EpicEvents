import click

class RegisterView:

    def print_password_error(self):
        click.echo(f"Les mots de passe ne matchent pas.")

    def success_message(self, first_name, last_name):
        click.echo(f"Inscription réussie pour {first_name} {last_name}.")

    def message_email_exists(self):
        click.echo("Cet email est déjà utilisé.")