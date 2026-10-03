import json
from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.models.userModel import Role, RoleEnum
from app.seed import seed_service
from main import app


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=test_engine)
    with TestingSessionLocal() as session:
        yield session
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.pop(get_db, None)


def test_seed_roles_is_idempotent_and_uses_json(
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    roles = [
        {"id": 1, "name": "admin", "description": "Administrator"},
        {"id": 2, "name": "develop", "description": "Developer"},
    ]
    roles_file = tmp_path / "roles.json"
    roles_file.write_text(json.dumps(roles), encoding="utf-8")
    monkeypatch.setattr(seed_service, "ROLES_FILE", roles_file)

    assert seed_service.seed_roles(db) == {"created": 2, "updated": 0, "total": 2}
    assert seed_service.seed_roles(db) == {"created": 0, "updated": 2, "total": 2}
    assert db.query(Role).count() == 2
    assert db.query(Role).filter(Role.name == RoleEnum.ADMIN).one().id == 1
