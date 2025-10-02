
from click.testing import CliRunner
from tests.integration_tests.helpers import create_test_user, \
    add_client_in_database

from datetime import datetime


def test_login_and_read_data(cli, db_session):
    runner = CliRunner()

    # Email unique pour éviter le conflit
    unique_email = f"test_{int(datetime.now().timestamp())}@example.com"

    user = create_test_user(db_session, email=unique_email)

    result = runner.invoke(cli, [
        'login',
        '--email', user.email_address,
        '--password', 'Password123!'
    ], obj={"session": db_session, "SECRET_KEY": "secret"})

    assert result.exit_code == 0
    assert "Welcome Test User!" in result.output

    client = add_client_in_database(db_session)

    result = runner.invoke(cli, [
        'list-clients'
    ], obj={"session": db_session, "SECRET_KEY": "secret"})

    assert result.exit_code == 0
    assert client.company in result.output
