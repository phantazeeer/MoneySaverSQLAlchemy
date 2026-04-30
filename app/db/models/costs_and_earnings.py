from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, CheckConstraint
from datetime import datetime, timezone

class CostsAndEarnings(Base):
    __tablename__ = "costs_and_earnings"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete="CASCADE"))
    operation_type: Mapped[int] = mapped_column(CheckConstraint('operation_type = 1 or operation_type = 0'))
    value: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(nullable=True, default="")
    category: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(tz=timezone.utc))

    user: Mapped["User"] = relationship(back_populates="costs_and_earnings")
    category: Mapped["Category"] = relationship(back_populates="costs_and_earnings")
