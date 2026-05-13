from datetime import date

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserLimits(Base):
    __tablename__ = "limits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    value: Mapped[int] = mapped_column(nullable=False, default=0)
    period: Mapped[str] = mapped_column(CheckConstraint("period IN ('day', 'week', 'month')"), nullable=True)
    start: Mapped[date] = mapped_column(nullable=False)
    end: Mapped[date] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))

    __table_args__ = (UniqueConstraint("user_id", "name", name="ix_limit_user_name"),)

    categlimits: Mapped[list["CategoriesLimits"]] = relationship(
        back_populates="limit",
        lazy="selectin",
        uselist=True,
        passive_deletes=True,
    )


# 2026-05-10 10:40:18.135208
