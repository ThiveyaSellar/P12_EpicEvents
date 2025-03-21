from sqlalchemy import ForeignKey, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
from datetime import date

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .event import Event

class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email_address: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(12))
    company: Mapped[str] = mapped_column(String(100))
    creation_date: Mapped[date] = mapped_column(Date)
    last_update: Mapped[date] = mapped_column(Date)
    commercial_id = mapped_column(ForeignKey("user.id"))

    commercial: Mapped["User"] = relationship(back_populates="clients")
    events: Mapped[List["Event"]] = relationship(back_populates="client")