from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.batcheModel import Batch, BatchStatusEnum
from app.models.farmModel import Farm
from app.models.userModel import RoleEnum, User
from app.schemas.batchSchema import BatchCreate, BatchStatusUpdate, BatchUpdate


ALLOWED_STATUS_TRANSITIONS: dict[BatchStatusEnum, set[BatchStatusEnum]] = {
    BatchStatusEnum.DRAFT: {
        BatchStatusEnum.FUNDING,
        BatchStatusEnum.CANCELLED,
    },
    BatchStatusEnum.FUNDING: {BatchStatusEnum.FUNDED},
    BatchStatusEnum.FUNDED: {BatchStatusEnum.IN_PROGRESS},
    BatchStatusEnum.IN_PROGRESS: {BatchStatusEnum.READY_FOR_SALE},
    BatchStatusEnum.READY_FOR_SALE: {BatchStatusEnum.CLOSED},
    BatchStatusEnum.CLOSED: set(),
    BatchStatusEnum.CANCELLED: set(),
}


class BatchService:
    @staticmethod
    def _generate_code() -> str:
        return f"BATCH-{uuid4().hex.upper()}"

    @staticmethod
    def _get_batch(db: Session, batch_id: int) -> Batch:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if batch is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El lote no existe.",
            )
        return batch

    @staticmethod
    def _can_manage_batch(batch: Batch, current_user: User) -> bool:
        return current_user.role.name == RoleEnum.ADMIN or (
            batch.farm.user_id == current_user.id
        )

    @staticmethod
    def _ensure_can_manage(batch: Batch, current_user: User) -> None:
        if not BatchService._can_manage_batch(batch, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para administrar este lote.",
            )

    @staticmethod
    def create_batch(
        db: Session, batch_create: BatchCreate, current_user: User
    ) -> Batch:
        farm = db.query(Farm).filter(Farm.id == batch_create.farm_id).first()
        if farm is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La finca no existe.",
            )
        if (
            current_user.role.name != RoleEnum.ADMIN
            and farm.user_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el propietario de la finca o un administrador puede crear lotes.",
            )

        batch = Batch(
            title=batch_create.title,
            description=batch_create.description,
            target_amount=batch_create.target_amount,
            duration_months=batch_create.duration_months,
            funding_start_date=batch_create.funding_start_date,
            farm_id=batch_create.farm_id,
            code=BatchService._generate_code(),
            status=BatchStatusEnum.DRAFT,
            price_per_share=0,
            estimated_roi_percentage=0,
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
        return batch

    @staticmethod
    def update_batch(
        db: Session,
        batch_id: int,
        batch_update: BatchUpdate,
        current_user: User,
    ) -> Batch:
        batch = BatchService._get_batch(db, batch_id)
        BatchService._ensure_can_manage(batch, current_user)
        if batch.status != BatchStatusEnum.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se puede editar un lote en estado DRAFT.",
            )

        for field, value in batch_update.model_dump(exclude_unset=True).items():
            setattr(batch, field, value)
        db.commit()
        db.refresh(batch)
        return batch

    @staticmethod
    def update_status(
        db: Session,
        batch_id: int,
        status_update: BatchStatusUpdate,
        current_user: User,
    ) -> Batch:
        batch = BatchService._get_batch(db, batch_id)
        BatchService._ensure_can_manage(batch, current_user)
        allowed_statuses = ALLOWED_STATUS_TRANSITIONS[batch.status]
        if status_update.status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"No se puede cambiar el lote de {batch.status.value} "
                    f"a {status_update.status.value}."
                ),
            )
        batch.status = status_update.status
        db.commit()
        db.refresh(batch)
        return batch
