from sqlalchemy import create_engine, text, Column, ForeignKey, Integer, String, Date, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship
import bcrypt

class Base(DeclarativeBase):
    pass

class Department(Base):

    __tablename__ = 'department'

    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    users = relationship('User', backref="users")

class User(Base):
    __tablename__ = 'user'

    id_user = Column(Integer, primary_key=True)
    _password = Column("password", String(128), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email_address = Column(String(100))
    phone = Column(String(12))
    id_department = Column(Integer, ForeignKey('department.id'))
    department = relationship('Department')
    contracts = relationship('Contract', backref="contracts")
    clients = relationship('Client', backref="clients")

    @property
    def password(self):
        raise AttributeError(
            "Le mot de passe n'est pas accessible directement."
        )

    @password.setter
    def password(self, plain_password: str):
        # Hache le mot de passe avant de le stocker
        self._password = bcrypt.hashpw(plain_password.encode('utf-8'),
                                       bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, plain_password: str) -> bool:
        # Vérifie si le mot de passe fourni correspond au hachage
        return bcrypt.checkpw(plain_password.encode('utf-8'),
                              self._password.encode('utf-8'))

    def __repr__(self):
        return f'User {self.name}'


class Client(Base):
    __tablename__ = "client"

    first_name = Column(String(100))
    last_name = Column(String(100))
    email_address = Column(String(100))
    phone = Column(String(12))
    company = Column(String(100))
    creation_date = Column(Date)
    last_update = Column(Date)
    id_commercial = Column(Integer, ForeignKey('user.id_user'))
    commercial = relationship('User')


class Contract(Base):
    __tablename__ = "contract"

    idContract = Column(Integer, primary_key=True)
    total_amount = Column(Integer)
    remaining_amount = Column(Integer)
    creation_date =  Column(Date)
    is_signed = Column(Boolean)
    id_commercial = Column(Integer, ForeignKey('user.id_user'))
    commercial = relationship('User')

class Event(Base):
    __tablename__ = "event"

    id_event = Column(Integer, primary_key=True)
    name = Column(String(100))
    start_date =  Column(Date)
    end_date =  Column(Date)
    address = Column(String(100))
    nb_attendees = Column(Integer)
    notes = Column(String(100))
    id_client = Column(Integer, ForeignKey('user.id_client'))
    client = relationship('Client')
    id_support = Column(Integer, ForeignKey('user.id_user'))
    support = relationship('User')
    id_contract = Column(Integer, ForeignKey('contract.id_contract'))
    contract = relationship('Contract')


