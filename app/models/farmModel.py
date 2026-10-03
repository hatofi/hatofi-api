
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.batcheModel import Batch
    from app.models.userModel import User

class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False) # nombre finca
    location: Mapped[str] = mapped_column(String(255), nullable=False) # ubicación geográfica de la finca (ej. Colombia, Antioquia, Remedios)
    capacity_head_count: Mapped[int] = mapped_column(nullable=False) # capacidad máxima de cabezas de ganado que la finca puede albergar
    capacity_current_head_count: Mapped[int] = mapped_column(nullable=False, default=0) # cantidad actual de cabezas de ganado en la finca
    
    # ID del usuario con rol 'FARMER'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    # Relaciones
    user: Mapped["User"] = relationship("User", back_populates="farms")
    batches: Mapped[list["Batch"]] = relationship(
        "Batch", # tabla relacionada
        back_populates="farm", # nombre del atributo en la clase Batch que hace referencia a esta relación
        cascade="all, delete-orphan", # indica que si se elimina una finca, también se eliminarán todos los lotes asociados a ella, y si un lote se elimina de la lista de lotes de la finca, también se eliminará de la base de datos. Esto ayuda a mantener la integridad referencial y evita registros huérfanos en la tabla de lotes.
    )