
from click.testing import CliRunner
from tests.integration_tests.helpers import create_test_user, add_client_in_database


def test_login_and_read_data(cli, db_session):
    runner = CliRunner()
    user = create_test_user(db_session)
    result = runner.invoke(cli, [
        'login',
        '--email', user.email_address,
        '--password', 'Password123!'
    ], obj={"session": db_session, "SECRET_KEY": "testsecret"})
    assert result.exit_code == 0
    assert "Welcome Test User!" in result.output
    client = add_client_in_database(db_session)
    result = runner.invoke(cli, [
        'list-clients'
    ], obj={"session": db_session, "SECRET_KEY": "testsecret"})
    assert result.exit_code == 0
    assert client.company in result.output


