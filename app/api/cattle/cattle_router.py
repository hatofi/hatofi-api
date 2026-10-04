from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.auth.auth_token import get_current_user
from app.api.cattle.cattle_services import CattleService
from app.core.database import get_db
from app.models.userModel import User
from app.schemas.cattleSchema import (
    CattleCreate,
    CattleResponse,
    CattleSalePriceUpdate,
    CattleWeightUpdate,
)

router = APIRouter(prefix="/cattle", tags=["Cattle"])


@router.post("", response_model=CattleResponse, status_code=status.HTTP_201_CREATED)
def create_cattle(
    cattle: CattleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CattleResponse:
    return CattleService.create_cattle(db, cattle, current_user)


@router.patch("/{cattle_id}/weight", response_model=CattleResponse)
def update_cattle_weight(
    cattle_id: int,
    update: CattleWeightUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CattleResponse:
    return CattleService.update_weight(db, cattle_id, update, current_user)


@router.patch("/{cattle_id}/sale-price", response_model=CattleResponse)
def update_cattle_sale_price(
    cattle_id: int,
    update: CattleSalePriceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CattleResponse:
    return CattleService.update_sale_price(db, cattle_id, update, current_user)