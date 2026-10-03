from fastapi import FastAPI

from app.api.user.userRouter import router as user_router
from app.core.database import Base, engine
from app.models import userModel as _user_model


def _load_models() -> None:
    _ = (_user_model.Role, _user_model.User)


_load_models()
Base.metadata.create_all(bind=engine)


app = FastAPI(title="Hatofi API", description="API for Hatofi application", version="0.0.1")
app.include_router(user_router)
