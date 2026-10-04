from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.batchModel import Batch


class Cattle(Base):
    __tablename__ = "cattle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ear_tag_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # código único de identificación del ganado (ej. número de arete)
    breed: Mapped[str] = mapped_column(String(50), nullable=False) # raza del ganado (ej. Angus, Brahman, Holstein)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # descripción adicional del ganado (ej. características, historial de salud, etc.)
    initial_weight_kg: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False) # peso inicial del ganado en kilogramos al momento de la compra
    current_weight_kg: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=0.00) # peso actual del ganado en kilogramos, se actualizará con cada registro de peso
    purchase_price: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False) # precio de compra del ganado en la moneda local o en la criptomoneda utilizada para la inversión
    sale_price: Mapped[Optional[float]] = mapped_column(Numeric(18, 2), nullable=True) # precio de venta del ganado en la moneda local o en la criptomoneda utilizada para la inversión, se registrará al momento de la venta
    batch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("batches.id", ondelete="CASCADE"),
        nullable=False) # referencia al lote al que pertenece el ganado
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) # fecha y hora en que se registró el ganado, con valor por defecto a la fecha y hora actual

    batch: Mapped["Batch"] = relationship("Batch", back_populates="cattle")
    weight_logs: Mapped[list["CattleWeightLog"]] = relationship(
        "CattleWeightLog",
        back_populates="cattle",
        cascade="all, delete-orphan",
        order_by="CattleWeightLog.logged_at",
    )


class CattleWeightLog(Base):
    __tablename__ = "cattle_weight_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cattle_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cattle.id", ondelete="CASCADE"),
        nullable=False) # Referencia al ganado
    weight_kg: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False) # Peso registrado en kilogramos
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Notas adicionales sobre el registro de peso (ej. condiciones de salud, alimentación, etc.)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()) # Fecha y hora en que se registró el peso, con valor por defecto a la fecha y hora actual

    cattle: Mapped["Cattle"] = relationship("Cattle", back_populates="weight_logs")
