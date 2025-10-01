from datetime import date

from argon2 import PasswordHasher
from models import User, Client


def create_test_user(
        session,
        email='test@example.com',
        password='Password123!'
):
    ph = PasswordHasher()
    hashed = ph.hash(password)
    user = User(
        email_address=email,
        password=hashed,
        first_name='Test',
        last_name='User',
        phone='0123456789',
        team_id=1
    )
    session.add(user)
    session.commit()
    return user


def add_client_in_database(session):
    client = Client(
        first_name="test",
        last_name="test",
        email_address="test@test.com",
        phone="0102030405",
        company="Woof Company",
        creation_date=date.today(),
        last_update=date.today(),
        commercial_id=1
    )
    session.add(client)
    session.commit()
    return client
