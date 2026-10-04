from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.models.farmModel import Farm
from app.models.userModel import Role, RoleEnum, User
from main import app


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=test_engine)
    with TestingSessionLocal() as db:
        roles = {
            role: Role(name=role, description=role.value)
            for role in (RoleEnum.ADMIN, RoleEnum.FARMER, RoleEnum.INVESTOR)
        }
        db.add_all(roles.values())
        db.flush()
        db.add_all(
            [
                User(
                    full_name="Admin",
                    email="admin@example.com",
                    hashed_password="hash",
                    role=roles[RoleEnum.ADMIN],
                ),
                User(
                    full_name="Farmer",
                    email="farmer@example.com",
                    hashed_password="hash",
                    role=roles[RoleEnum.FARMER],
                ),
                User(
                    full_name="Investor",
                    email="investor@example.com",
                    hashed_password="hash",
                    role=roles[RoleEnum.INVESTOR],
                ),
            ]
        )
        db.flush()
        db.add(
            Farm(
                name="Farm",
                location="Antioquia",
                capacity_head_count=100,
                capacity_current_head_count=0,
                user_id=2,
            )
        )
        db.commit()
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.pop(get_db, None)


def auth_headers(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token({'sub': str(user_id)})}"}


def batch_payload() -> dict:
    return {
        "title": "Lote inicial",
        "description": "Lote de prueba",
        "target_amount": 10000,
        "duration_months": 18,
        "funding_start_date": "2026-11-01T00:00:00",
        "farm_id": 1,
    }


def test_owner_can_create_edit_and_change_batch_status(
    client: TestClient,
) -> None:
    response = client.post(
        "/batches", json=batch_payload(), headers=auth_headers(2)
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "DRAFT"
    assert data["code"].startswith("BATCH-")
    batch_id = data["id"]

    update = client.patch(
        f"/batches/{batch_id}",
        json={"description": "Descripción actualizada"},
        headers=auth_headers(2),
    )
    assert update.status_code == 200
    assert update.json()["description"] == "Descripción actualizada"

    for next_status in ("FUNDING", "FUNDED", "IN_PROGRESS", "READY_FOR_SALE", "CLOSED"):
        status_response = client.patch(
            f"/batches/{batch_id}/status",
            json={"status": next_status},
            headers=auth_headers(2),
        )
        assert status_response.status_code == 200
        assert status_response.json()["status"] == next_status

    locked_update = client.patch(
        f"/batches/{batch_id}",
        json={"title": "No debe cambiar"},
        headers=auth_headers(2),
    )
    assert locked_update.status_code == 409


def test_admin_can_edit_and_owner_rules_are_enforced(client: TestClient) -> None:
    created = client.post(
        "/batches", json=batch_payload(), headers=auth_headers(2)
    )
    batch_id = created.json()["id"]

    admin_update = client.patch(
        f"/batches/{batch_id}",
        json={"title": "Editado por admin"},
        headers=auth_headers(1),
    )
    assert admin_update.status_code == 200

    investor_create = client.post(
        "/batches", json=batch_payload(), headers=auth_headers(3)
    )
    assert investor_create.status_code == 403


def test_status_transitions_reject_invalid_jumps_and_allow_cancel(
    client: TestClient,
) -> None:
    created = client.post(
        "/batches", json=batch_payload(), headers=auth_headers(2)
    )
    batch_id = created.json()["id"]

    invalid = client.patch(
        f"/batches/{batch_id}/status",
        json={"status": "FUNDED"},
        headers=auth_headers(2),
    )
    assert invalid.status_code == 409

    cancelled = client.patch(
        f"/batches/{batch_id}/status",
        json={"status": "CANCELLED"},
        headers=auth_headers(2),
    )
    assert cancelled.status_code == 200

    terminal_jump = client.patch(
        f"/batches/{batch_id}/status",
        json={"status": "FUNDING"},
        headers=auth_headers(2),
    )
    assert terminal_jump.status_code == 409
