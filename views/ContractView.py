import click

class ContractView:

    @staticmethod
    def show_all_contracts(contracts):
        click.echo("------------- Contracts -------------")
        for contract in contracts:
            click.echo(f"{contract.total_amount} {contract.remaining_amount}")