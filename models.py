from sqlalchemy import create_engine, text, Column, ForeignKey, Integer, String, Date, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List

class Base(DeclarativeBase):
    pass

class Team(Base):
    __tablename__ = "team"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))

    users: Mapped[List["User"]] = relationship(back_populates="team")

class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email_address: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(12))
    team_id = mapped_column(ForeignKey("team.id"))

    team: Mapped[Team] = relationship(back_populates="users")
    clients: Mapped[List["Client"]] = relationship(back_populates="commercial")
    contracts: Mapped[List["Contract"]] = relationship(back_populates="commercial")
    events: Mapped[List["Event"]] = relationship(back_populates="support")

class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email_address: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(12))
    company: Mapped[str] = mapped_column(String(100))
    creation_date:Mapped[Date] = mapped_column(Date)
    last_update: Mapped[Date] = mapped_column(Date)
    commercial_id = mapped_column(ForeignKey("user.id"))

    commercial: Mapped[User] = relationship(back_populates="clients")
    events: Mapped[List["Events"]] = relationship(back_populates="client")

class Contract(Base):
    __tablename__ = "contract"

    id: Mapped[int] = mapped_column(primary_key=True)
    total_amount: Mapped[int] = mapped_column(nullable=False)
    remaining_amount: Mapped[int] = mapped_column(Integer, nullable=True)
    creation_date: Mapped[Date] = mapped_column(Date)
    is_signed: Mapped[Boolean] = mapped_column(Boolean, nullable=False)
    commercial_id = mapped_column(ForeignKey("user.id"))

    commercial: Mapped[User] = relationship(back_populates="contracts")
    event: Mapped["Event"] = relationship(back_populates="contract", uselist=False)

class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    start_date: Mapped[Date] = mapped_column(Date)
    end_date: Mapped[Date] = mapped_column(Date)
    address: Mapped[str] = mapped_column(String(100))
    nb_attendees: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str] = mapped_column(String(100))
    client_id = mapped_column(ForeignKey("client.id"))
    support_id = mapped_column(ForeignKey("user.id"))
    contract_id = mapped_column(ForeignKey("contract.id"))

    client: Mapped[Client] = relationship(back_populates="events")
    support: Mapped[User] = relationship(back_populates="events")
    contract: Mapped[Contract] = relationship(back_populates="event")



