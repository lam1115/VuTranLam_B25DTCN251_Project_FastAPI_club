from fastapi import FastAPI

from app.db.database import Base, engine
from app.models import (
    Club_activitiesModel,
    Activity_logsModel,
    AttachmentsModel,
    Refresh_tokensModel,
    Club_membersModel,
    ClubModel,
    UserModel,
    CommentsModel,
)

from app.core import AppException, app_exception_handler

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_exception_handler(AppException, app_exception_handler)


# Health check endpoint
@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok", "message": "Service is running healthy"}
