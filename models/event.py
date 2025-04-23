from sqlalchemy import ForeignKey, String, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from datetime import date

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .client import Client
    from .contract import Contract

class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    address: Mapped[str] = mapped_column(String(100))
    nb_attendees: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str] = mapped_column(String(100))
    client_id = mapped_column(ForeignKey("client.id"))
    support_id = mapped_column(ForeignKey("user.id"))
    contract_id = mapped_column(ForeignKey("contract.id"))

    client: Mapped["Client"] = relationship(back_populates="events")
    support: Mapped["User"] = relationship(back_populates="events")
    contract: Mapped["Contract"] = relationship(back_populates="event")

    def __str__(self):
        return (
            f"Event: {self.name}\n"
            f"Date: {self.start_date} → {self.end_date}\n"
            f"Address: {self.address}\n"
            f"Attendees: {self.nb_attendees}\n"
            f"Client: {self.client.company if self.client else 'N/A'}\n"
        )