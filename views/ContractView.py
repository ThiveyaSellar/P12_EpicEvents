import click

class ContractView:

    @staticmethod
    def show_all_contracts(contracts):
        row_format = "{:<5} {:<15} {:<20} {:<12} {:<10} {:<12}"
        headers = (
            "Id", "Total Amount", "Remaining Amount", "Date", "Signed",
            "Commercial"
        )
        click.echo(row_format.format(*headers))
        click.echo("-" * 90)

        for contract in contracts:
            click.echo(row_format.format(
                contract.id,
                contract.total_amount,
                contract.remaining_amount if contract.remaining_amount is not None else "N/A",
                contract.creation_date.strftime("%Y-%m-%d"),
                "Yes" if contract.is_signed else "No",
                f"{contract.commercial.first_name} {contract.commercial.last_name}" if contract.commercial else "N/A",
            ))