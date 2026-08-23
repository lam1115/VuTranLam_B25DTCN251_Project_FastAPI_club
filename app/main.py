from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.db.database import Base, engine
from app.routers.authentication_router import router as authentication
from app.routers.user_router import router as user
from app.routers.club_router import router as club
from app.core.limiter import limit


from app.core import AppException, app_exception_handler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="STUDENT CLUB MANAGEMENT API")

app.state.limiter = limit
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_exception_handler(AppException, app_exception_handler)


app.include_router(authentication)
app.include_router(user)
app.include_router(club)


# Health check endpoint
@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok", "message": "Service is running healthy"}
