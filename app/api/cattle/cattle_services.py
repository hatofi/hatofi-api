from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.batchModel import Batch, BatchStatusEnum
from app.models.cattleModel import Cattle, CattleWeightLog
from app.models.userModel import RoleEnum, User
from app.schemas.cattleSchema import (
    CattleCreate,
    CattleSalePriceUpdate,
    CattleWeightUpdate,
)


class CattleService:
    @staticmethod
    def _get_cattle(db: Session, cattle_id: int) -> Cattle:
        cattle = db.query(Cattle).filter(Cattle.id == cattle_id).first()
        if cattle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El ganado no existe.",
            )
        return cattle

    @staticmethod
    def _ensure_farm_owner(cattle: Cattle, current_user: User) -> None:
        if cattle.batch.farm.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el propietario de la finca puede actualizar el peso.",
            )

    @staticmethod
    def create_cattle(
        db: Session, cattle_create: CattleCreate, current_user: User
    ) -> Cattle:
        batch = db.query(Batch).filter(Batch.id == cattle_create.batch_id).first()
        if batch is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El lote no existe.",
            )
        if batch.status != BatchStatusEnum.BUYING_PROCESS:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No es posible iniciar la compra porque el lote no está en estado BUYING_PROCESS.",
            )
        if (
            current_user.role.name != RoleEnum.ADMIN
            and batch.farm.user_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el propietario de la finca o un administrador puede registrar ganado.",
            )

        cattle = Cattle(
            ear_tag_code=cattle_create.ear_tag_code,
            breed=cattle_create.breed,
            description=cattle_create.description,
            initial_weight_kg=cattle_create.initial_weight_kg,
            current_weight_kg=cattle_create.initial_weight_kg,
            purchase_price=cattle_create.purchase_price,
            batch_id=cattle_create.batch_id,
            weight_logs=[
                CattleWeightLog(
                    weight_kg=cattle_create.initial_weight_kg,
                    notes=cattle_create.notes,
                )
            ],
        )
        db.add(cattle)
        db.commit()
        db.refresh(cattle)
        return cattle

    @staticmethod
    def update_weight(
        db: Session,
        cattle_id: int,
        weight_update: CattleWeightUpdate,
        current_user: User,
    ) -> Cattle:
        cattle = CattleService._get_cattle(db, cattle_id)
        CattleService._ensure_farm_owner(cattle, current_user)
        cattle.current_weight_kg = weight_update.current_weight_kg
        cattle.weight_logs.append(
            CattleWeightLog(
                weight_kg=weight_update.current_weight_kg,
                notes=weight_update.notes,
            )
        )
        db.commit()
        db.refresh(cattle)
        return cattle

    @staticmethod
    def update_sale_price(
        db: Session,
        cattle_id: int,
        sale_price_update: CattleSalePriceUpdate,
        current_user: User,
    ) -> Cattle:
        cattle = CattleService._get_cattle(db, cattle_id)
        if current_user.role.name != RoleEnum.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo un administrador puede actualizar el precio de venta.",
            )
        cattle.sale_price = sale_price_update.sale_price
        db.commit()
        db.refresh(cattle)
        return cattle