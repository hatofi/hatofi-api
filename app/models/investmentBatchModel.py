from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.batcheModel import Batch
    from app.models.userModel import User


class InvestmentBatch(Base):
    """Association between an investor and an investment batch."""

    __tablename__ = "investment_batches"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    batch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("batches.id", ondelete="CASCADE"),
        primary_key=True,
    )

    investor: Mapped["User"] = relationship("User", back_populates="investments")
    batch: Mapped["Batch"] = relationship("Batch", back_populates="investments")
