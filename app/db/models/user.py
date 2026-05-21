from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    balance: Mapped[int] = mapped_column(nullable=False, default=0)
    username: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    goal_name: Mapped[str] = mapped_column(nullable=True)
    goal_value: Mapped[int] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc).replace(tzinfo=None))

    costs_and_earnings: Mapped[list["CostsAndEarnings"]] = relationship(back_populates="user")
