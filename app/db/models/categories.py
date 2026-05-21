from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))

    __table_args__ = (UniqueConstraint("user_id", "name", name="ix_category_user_name"),)

    costs_and_earnings: Mapped["CostsAndEarnings"] = relationship(back_populates="category")
    categlimits: Mapped[list["CategoriesLimits"]] = relationship(
        back_populates="category",
        lazy="selectin",
        uselist=True,
        passive_deletes=True,
    )
