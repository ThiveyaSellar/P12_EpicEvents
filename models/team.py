from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .user import User

class Team(Base):
    __tablename__ = "team"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))

    users: Mapped[List["User"]] = relationship(back_populates="team")