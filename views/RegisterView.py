import click


class RegisterView:

    @staticmethod
    def print_password_error():
        click.echo(f"Passwords don't match.")

    @staticmethod
    def success_message(first_name, last_name):
        click.echo(f"Registration is successful for {first_name} {last_name}.")

    @staticmethod
    def message_email_exists():
        click.echo("An account with this email already exists.")

    @staticmethod
    def message_registration_failed(errors):
        click.echo("Registration has failed.")
        click.echo(errors)

    @staticmethod
    def message_db_error(errors):
        # Affiche proprement même si errors est une liste ou autre
        if isinstance(errors, list):
            for e in errors:
                click.echo(str(e))
        else:
            click.echo(str(errors))