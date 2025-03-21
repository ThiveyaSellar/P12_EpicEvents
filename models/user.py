from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from .base import Base

# Imports conditionnels pour éviter les imports circulaires
if TYPE_CHECKING:
    from .team import Team
    from .client import Client
    from .contract import Contract
    from .event import Event

class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    token: Mapped[str] = mapped_column(String(512), nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email_address: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(12))
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"))

    team: Mapped["Team"] = relationship(back_populates="users")
    clients: Mapped[List["Client"]] = relationship(back_populates="commercial")
    contracts: Mapped[List["Contract"]] = relationship(back_populates="commercial")
    events: Mapped[List["Event"]] = relationship(back_populates="support")