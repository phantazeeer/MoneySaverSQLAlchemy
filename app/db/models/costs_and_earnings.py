from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CostsAndEarnings(Base):
    __tablename__ = "costs_and_earnings"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    operation_type: Mapped[int] = mapped_column(CheckConstraint("operation_type = 1 or operation_type = 0"))
    value: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(nullable=True, default="")
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc).replace(tzinfo=None))

    user: Mapped["User"] = relationship(back_populates="costs_and_earnings")
    category: Mapped["Category"] = relationship(back_populates="costs_and_earnings", lazy="selectin")
