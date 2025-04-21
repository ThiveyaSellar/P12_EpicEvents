import click

class ClientView:

    @staticmethod
    def show_all_clients(clients):
        click.echo("------------- Clients -------------")
        for client in clients:
            click.echo(f"{client.first_name} {client.last_name}")