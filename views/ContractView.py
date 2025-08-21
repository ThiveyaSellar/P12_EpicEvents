import re

import click

from views.UserView import UserView


class ContractView:

    @staticmethod
    def show_contracts(contracts):
        if len(contracts) == 0:
            click.echo("No contracts found.")
            return
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

    @staticmethod
    def select_event_for_contract(event_ids):
        id = click.prompt(
            f"For which event ? {event_ids} [Enter to skip]", default=None)
        if id is None:
            return
        while not id.isdigit() or int(id) not in event_ids:
            click.echo("Verify the event ID. The event must exist and must not be linked to any contract.")
            id = click.prompt(f"For which event ? {event_ids} [Enter to skip]",
                              default=None)
            if id is None:
                return
        return int(id)

    @staticmethod
    def ask_amounts(contract=None):

        total_default = contract.total_amount if contract else None
        remaining_default = contract.remaining_amount if contract else None

        while True:
            total_amount = click.prompt("Total amount", type=int,
                                        default=total_default,
                                        show_default=total_default is not None)
            if total_amount <= 0:
                click.echo("Total amount must be greater than 0.")
                continue
            remaining_amount = click.prompt("Remaining amount", type=int,
                                            default=remaining_default,
                                            show_default=remaining_default is not None)
            if remaining_amount <= 0:
                click.echo("Remaining amount must be greater than or equal to 0.")
                continue
            if remaining_amount <= total_amount and total_amount > 0:
                break
            if remaining_amount > total_amount:
                click.echo("Remaining amount must be less than or equal to total amount. Please try again.")
                continue
            click.echo("Please try again.")
        return total_amount, remaining_amount

    @staticmethod
    def get_new_contract_data():

        contract = {}
        click.echo("Enter new contract informations :")
        contract["total_amount"], contract["remaining_amount"] = ContractView.ask_amounts()
        contract["is_signed"] = click.confirm("Is it signed?", default=False)

        return contract

    @staticmethod
    def validate_phone(ctx, param, value):
        phone = value
        pattern = r"^0[1-9](\d{2}){4}$"
        if not re.match(pattern, phone):
            raise click.BadParameter("The phone number start with the digit 0 and must have 10 digits.")
        return phone

    @staticmethod
    def get_updating_contract(contract_ids):
        if not contract_ids:
            click.echo("No contracts.")
            return
        id = click.prompt(
            "Which contract do you want to update ? [Enter to skip]", default="", show_default=False)
        if id == "":
            return
        while not id.isdigit() or int(id) not in contract_ids:
            click.echo("Invalid id.")
            id = click.prompt(
                "Which contract do you want to update ? [Enter to skip]", show_default=False,
                default="")
            if id == "":
                return
        return int(id)

    @staticmethod
    def get_contract_new_data(contract, sales_reps):
        if contract is None:
            click.echo("contract not existent, can't be updated.")
            return
        click.echo(
            "Enter new data or press [Enter] to keep the current value:")
        # Pour chaque champ, on propose la valeur actuelle
        contract.total_amount, contract.remaining_amount = ContractView.ask_amounts()
        contract.is_signed = click.confirm("Is it signed ?",
                                            default=contract.is_signed)

        new_commercial_id = UserView.ask_change_sales_rep(contract, sales_reps)
        if new_commercial_id:
            contract.commercial_id = new_commercial_id

        return contract

    @staticmethod
    def message_no_events_without_contracts():
        click.echo("All events have already a contract.")

    @staticmethod
    def message_adding_contract_failed(errors):
        click.echo("Contract has not been added.")
        click.echo(errors)

    @staticmethod
    def message_updating_contract_failed(errors):
        click.echo("Contract has not been updated.")
        click.echo(errors)

    @staticmethod
    def message_contract_added():
        click.echo("Contract has been added.")

    @staticmethod
    def message_contract_updated():
        click.echo("Contract has been updated.")

    @staticmethod
    def message_invalid_event():
        click.echo("Invalid event.")

    @staticmethod
    def message_no_contract():
        click.echo("Found no contract.")

    @staticmethod
    def message_action_not_permitted():
        click.echo(
            "Only members of the Sales team are allowed to update a contract.")
