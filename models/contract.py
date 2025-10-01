from sqlalchemy import ForeignKey, Integer, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from datetime import date

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .event import Event


class Contract(Base):
    __tablename__ = "contract"

    id: Mapped[int] = mapped_column(primary_key=True)
    total_amount: Mapped[int] = mapped_column(nullable=False)
    remaining_amount: Mapped[int] = mapped_column(Integer, nullable=True)
    creation_date: Mapped[date] = mapped_column(Date)
    is_signed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    commercial_id = mapped_column(ForeignKey("user.id"))

    commercial: Mapped["User"] = relationship(back_populates="contracts")
    event: Mapped["Event"] = relationship(
        back_populates="contract", uselist=False
    )
