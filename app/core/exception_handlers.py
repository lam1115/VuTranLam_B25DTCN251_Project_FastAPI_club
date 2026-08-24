from datetime import datetime, timezone

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException


# Hàm format trả về lỗi
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "message": exc.message,
            "data": None,
            "error": exc.error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": request.url.path,
        },
    )
