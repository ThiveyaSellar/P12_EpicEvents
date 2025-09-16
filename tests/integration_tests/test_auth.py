from click.testing import CliRunner


def test_register_and_login(cli, db_session):
    runner = CliRunner()
    result = runner.invoke(cli, [
        'register',
        '--email', 'test@example.com',
        '--password', 'Password123!',
        '--password2', 'Password123!',
        '--first_name', 'Alice',
        '--last_name', 'Dupont',
        '--phone', '0123456789',
        '--team', 'Commercial'
    ], obj={"session": db_session, "SECRET_KEY": "testsecret"})
    assert result.exit_code == 0
    # assert "success" in result.output.lower() or result.output != ''
    assert "Registration is successful for Alice Dupont." in result.output
    result = runner.invoke(cli, [
        'login',
        '--email', 'test@example.com',
        '--password', 'Password123!'
    ], obj={"session": db_session, "SECRET_KEY": "testsecret"})
    assert result.exit_code == 0
    assert "Welcome Alice Dupont!" in result.output
