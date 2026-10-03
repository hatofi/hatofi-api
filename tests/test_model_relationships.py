from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.batcheModel import Batch
from app.models.farmModel import Farm
from app.models.investmentBatchModel import InvestmentBatch
from app.models.userModel import Role, RoleEnum, User


def test_user_farm_batch_and_investment_relationships() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        farmer_role = Role(name=RoleEnum.FARMER, description="Farmer")
        investor_role = Role(name=RoleEnum.INVESTOR, description="Investor")
        farmer = User(
            full_name="Farmer",
            email="farmer@example.com",
            hashed_password="hash",
            role=farmer_role,
        )
        investor_one = User(
            full_name="Investor One",
            email="investor1@example.com",
            hashed_password="hash",
            role=investor_role,
        )
        investor_two = User(
            full_name="Investor Two",
            email="investor2@example.com",
            hashed_password="hash",
            role=investor_role,
        )
        farm = Farm(
            name="Farm",
            location="Antioquia",
            capacity_head_count=100,
            user=farmer,
        )
        batch = Batch(
            title="Batch",
            code="BATCH-001",
            target_amount=1000,
            price_per_share=100,
            estimated_roi_percentage=10,
            duration_months=18,
            funding_start_date=datetime(2026, 1, 1),
            funding_end_date=datetime(2026, 2, 1),
            farm=farm,
        )
        batch.investments = [
            InvestmentBatch(investor=investor_one),
            InvestmentBatch(investor=investor_two),
        ]
        db.add(batch)
        db.commit()

        db.refresh(farmer)
        db.refresh(investor_one)
        db.refresh(batch)
        assert farmer.farms == [farm]
        assert farm.batches == [batch]
        assert {investment.investor for investment in batch.investments} == {
            investor_one,
            investor_two,
        }
        assert investor_one.investments[0].batch is batch

    Base.metadata.drop_all(bind=engine)
from datetime import datetime
