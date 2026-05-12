from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CategoriesLimits(Base):
    __tablename__ = "categorieslimits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    categ_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    limit_id: Mapped[int] = mapped_column(ForeignKey("limits.id", ondelete="CASCADE"))

    category: Mapped["Category"] = relationship(back_populates="categlimits", lazy="selectin")
    limit: Mapped["UserLimits"] = relationship(back_populates="categlimits", lazy="selectin")
