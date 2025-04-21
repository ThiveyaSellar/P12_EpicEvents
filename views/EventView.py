import click

class EventView:

    @staticmethod
    def show_all_events(events):
        click.echo("------------- Events -------------")
        for event in events:
            click.echo(f"{event.name} {event.end_date}")

    @staticmethod
    def show_support_events(events):
        click.echo("------------- Events -------------")
        for event in events:
            click.echo(f"{event.name} {event.end_date}")

