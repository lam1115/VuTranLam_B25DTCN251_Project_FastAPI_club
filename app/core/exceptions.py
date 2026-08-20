class AppException(Exception):
    def __init__(self, status_code: int, message: str, error: str):
        self.status_code = status_code
        self.message = message
        self.error = error


class NotFoundException(AppException):
    def __init__(self, message="Resource not found"):
        super().__init__(status_code=404, message=message, error="NOT_FOUND")


class BadRequestException(AppException):
    def __init__(self, message="Bad request"):
        super().__init__(status_code=400, message=message, error="BAD_REQUEST")


class UnauthorizedException(AppException):
    def __init__(self, message="Unauthorized"):
        super().__init__(status_code=401, message=message, error="UNAUTHORIZED")


class ForbiddenException(AppException):
    def __init__(self, message="Forbidden"):
        super().__init__(status_code=403, message=message, error="FORBIDDEN")
