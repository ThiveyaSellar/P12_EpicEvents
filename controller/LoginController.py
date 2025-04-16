import jwt, os
from models import User
from argon2 import PasswordHasher
from datetime import datetime, timedelta
from sqlalchemy.exc import NoResultFound

from utils.token_utils import  create_netrc_file, get_netrc_path, \
    update_tokens_in_netrc

from views.LoginView import LoginView

class LoginController:

    def check_user_mail(self, session, email):
        return session.query(User).filter_by(email_address=email).one()

    def define_token(self, user, SECRET_KEY, time):
        payload = {
            "user_id": user.id,
            "email": user.email_address,
            "role": user.team.name,
            "exp": datetime.now() + timedelta(hours=time)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token

    def write_in_netrc(self, access_token, refresh_token):
        netrc_path = get_netrc_path()
        machine = "127.0.0.1"
        if not os.path.exists(netrc_path):
            create_netrc_file(machine, access_token, refresh_token,
                              netrc_path)
        else:
            update_tokens_in_netrc(machine, access_token, refresh_token,
                                   netrc_path)

    def verify_password(self, ph, user_password, password):
        try:
            return ph.verify(user_password, password)
        except:
            return False

    def login(self, email, password, session, SECRET_KEY):
        loginView = LoginView()
        ph = PasswordHasher()

        try:
            user = self.check_user_mail(session, email)
        except NoResultFound:
            loginView.print_user_not_found()

        if not self.verify_password(ph, user.password, password):
            loginView.show_password_error()
            return

        access_token = self.define_token(user, SECRET_KEY, 1)
        refresh_token = self.define_token(user, SECRET_KEY, 3)

        user.token = refresh_token
        session.commit()

        self.write_in_netrc(access_token, refresh_token)
        loginView.print_welcome_message(user)
