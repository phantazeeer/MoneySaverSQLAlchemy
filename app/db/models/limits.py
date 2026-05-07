from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class UserLimits(Base):
    __tablename__ = "limits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[int] = mapped_column(nullable=False, default=0)
    period: Mapped[str] = mapped_column(CheckConstraint("period IN ('day', 'week', 'month')") , nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), unique=True)