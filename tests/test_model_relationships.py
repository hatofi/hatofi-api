from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.batchModel import Batch
from app.models.cattleModel import Cattle, CattleWeightLog
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
        cattle = Cattle(
            ear_tag_code="TAG-001",
            breed="Brahman",
            initial_weight_kg=350,
            current_weight_kg=380,
            purchase_price=2000,
            batch=batch,
        )
        cattle.weight_logs = [
            CattleWeightLog(weight_kg=350, notes="Initial weight"),
            CattleWeightLog(weight_kg=380, notes="Current weight"),
        ]
        db.add(batch)
        db.commit()

        db.refresh(farmer)
        db.refresh(investor_one)
        db.refresh(batch)
        db.refresh(cattle)
        assert farmer.farms == [farm]
        assert farm.batches == [batch]
        assert {investment.investor for investment in batch.investments} == {
            investor_one,
            investor_two,
        }
        assert investor_one.investments[0].batch is batch
        assert cattle.batch is batch
        assert batch.cattle == [cattle]
        assert len(cattle.weight_logs) == 2

    Base.metadata.drop_all(bind=engine)
