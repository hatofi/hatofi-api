from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.auth.auth_token import get_current_user
from app.api.investment.investment_services import InvestmentService
from app.core.database import get_db
from app.models.userModel import User
from app.schemas.investmentBatchSchema import (
    BatchInvestorResponse,
    InvestmentAmountUpdate,
    InvestmentCreate,
    InvestmentResponse,
    InvestmentSummary,
)

router = APIRouter(prefix="/investments", tags=["Investments"])


@router.post("", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
def invest(
    investment: InvestmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvestmentResponse:
    """Crear una nueva inversión para el usuario actual en el lote especificado."""
    return InvestmentService.invest(db, investment, current_user)


@router.patch("/{batch_id}/amount", response_model=InvestmentResponse)
def increase_investment(
    batch_id: int,
    update: InvestmentAmountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvestmentResponse:
    """Incrementar la inversión del usuario actual en un lote específico."""
    return InvestmentService.increase(db, batch_id, update, current_user)


@router.get("/me", response_model=list[InvestmentResponse])
def list_my_investments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[InvestmentResponse]:
    """Listar todas las inversiones del usuario actual."""
    return InvestmentService.list_mine(db, current_user)


@router.get("/me/summary", response_model=InvestmentSummary)
def investment_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvestmentSummary:
    """Obtener un resumen de las inversiones del usuario actual.
    Devuelve un diccionario con:
    - open_investments: número de inversiones abiertas (lotes no cerrados)
    - closed_investments: número de inversiones cerradas (lotes cerrados)
    - open_amount: monto total invertido en lotes abiertos
    - closed_amount: monto total invertido en lotes cerrados
    """
    return InvestmentService.summary(db, current_user)


@router.get("/me/{batch_id}", response_model=InvestmentResponse)
def get_my_investment(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvestmentResponse:
    """Obtener la inversión del usuario actual en un lote específico."""
    return InvestmentService.get_mine(db, batch_id, current_user)


@router.get(
    "/batch/{batch_id}/investors",
    response_model=list[BatchInvestorResponse],
)
def list_batch_investors(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BatchInvestorResponse]:
    """Consultar los inversores de un lote específico."""
    return InvestmentService.list_batch_investors(db, batch_id, current_user)
