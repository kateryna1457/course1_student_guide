import logging
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from psycopg2 import Error as PostgresError

from src.utils import ValidationError

logger = logging.getLogger(__name__)


class StudentNotFoundError(HTTPException):
    """Студент не знайдений."""

    def __init__(self, student_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )


class DuplicateStudentIDError(HTTPException):
    """Дублікат номера залікової книжки."""

    def __init__(self, student_id_number: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Student with ID number '{student_id_number}' already exists"
        )


class DatabaseError(HTTPException):
    """Помилка бази даних."""

    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


# Exception handlers


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handler для ValidationError.

    Args:
        request: FastAPI request
        exc: ValidationError exception

    Returns:
        JSONResponse: Відповідь з помилкою
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": str(exc),
            "error_type": "validation_error"
        }
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """
    Handler для ValueError (бізнес-правила).

    Args:
        request: FastAPI request
        exc: ValueError exception

    Returns:
        JSONResponse: Відповідь з помилкою
    """
    error_message = str(exc)

    # Check if it's a duplicate error
    if "already exists" in error_message:
        status_code = status.HTTP_409_CONFLICT
        error_type = "duplicate_error"
    # Check if it's a not found error
    elif "does not exist" in error_message or "not found" in error_message.lower():
        status_code = status.HTTP_404_NOT_FOUND
        error_type = "not_found_error"
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        error_type = "value_error"

    return JSONResponse(
        status_code=status_code,
        content={
            "detail": error_message,
            "error_type": error_type
        }
    )


async def postgres_error_handler(request: Request, exc: PostgresError) -> JSONResponse:
    """
    Handler для PostgresError.

    Args:
        request: FastAPI request
        exc: PostgresError exception

    Returns:
        JSONResponse: Відповідь з помилкою
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "error_type": "database_error",
            "error_code": exc.pgcode if hasattr(exc, 'pgcode') else None
        }
    )


async def request_validation_error_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handler для Pydantic RequestValidationError.

    Args:
        request: FastAPI request
        exc: RequestValidationError exception

    Returns:
        JSONResponse: Відповідь з помилкою
    """
    # Convert errors to serializable format
    errors = []
    for error in exc.errors():
        error_dict = {
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        }
        if "input" in error:
            error_dict["input"] = str(error["input"])
        errors.append(error_dict)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": errors,
            "error_type": "request_validation_error"
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler для HTTPException.

    Args:
        request: FastAPI request
        exc: HTTPException exception

    Returns:
        JSONResponse: Відповідь з помилкою
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_type": "http_exception"
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler для загальних винятків.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSONResponse: Відповідь з помилкою
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_type": "internal_error"
        }
    )
