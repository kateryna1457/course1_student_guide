"""
API роутер для роботи зі студентами.

Endpoints для CRUD операцій зі студентами.
"""

from typing import List
from fastapi import APIRouter, Query, status, Request
from fastapi.responses import FileResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import tempfile
import os
from datetime import datetime

from src.models import (
    StudentCreate,
    StudentUpdate,
    StudentFullInfoResponse,
    StudentSearchParams,
    PaginatedResponse
)
from src.services import StudentService
from src.api.exceptions import StudentNotFoundError
from src.constants import (
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_PERIOD,
    RATE_LIMIT_REQUESTS_CREATE,
    RATE_LIMIT_PERIOD_CREATE
)

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Створити router
router = APIRouter(prefix="/students", tags=["students"])

# Ініціалізувати сервіс
service = StudentService()


@router.post(
    "/",
    response_model=StudentFullInfoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Створити студента",
    description="Створити нового студента з валідацією даних"
)
@limiter.limit(f"{RATE_LIMIT_REQUESTS_CREATE}/{RATE_LIMIT_PERIOD_CREATE}")
async def create_student(request: Request, student_data: StudentCreate):
    """
    Створити нового студента.

    Args:
        student_data: Дані студента для створення

    Returns:
        StudentFullInfoResponse: Створений студент з повною інформацією

    Raises:
        422: Невалідні дані
        409: Номер залікової книжки вже існує
        500: Помилка бази даних
    """
    # Convert Pydantic model to dict
    data = student_data.model_dump()

    # Create student
    student_id = service.create_student(data)

    # Get created student with full info
    student = service.get_student(student_id)

    return student


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Список студентів",
    description="Отримати список студентів з пагінацією"
)
@limiter.limit(f"{RATE_LIMIT_REQUESTS}/{RATE_LIMIT_PERIOD}")
async def list_students(
    request: Request,
    offset: int = Query(0, ge=0, description="Зміщення"),
    limit: int = Query(50, ge=1, le=100, description="Кількість записів (макс 100)")
):
    """
    Отримати список студентів.

    Args:
        offset: Зміщення для пагінації
        limit: Кількість записів

    Returns:
        PaginatedResponse: Пагінована відповідь зі студентами
    """
    students, total = service.list_students(offset=offset, limit=limit)

    return PaginatedResponse(
        total=total,
        offset=offset,
        limit=limit,
        items=[s.to_dict() for s in students]
    )


@router.get(
    "/{student_id_number}",
    response_model=StudentFullInfoResponse,
    summary="Отримати студента",
    description="Отримати студента за номером залікової книжки з повною інформацією"
)
@limiter.limit(f"{RATE_LIMIT_REQUESTS}/{RATE_LIMIT_PERIOD}")
async def get_student(request: Request, student_id_number: str):
    """
    Отримати студента за номером залікової книжки.

    Args:
        student_id_number: Номер залікової книжки студента

    Returns:
        StudentFullInfoResponse: Студент з повною інформацією

    Raises:
        404: Студент не знайдений
    """
    student = service.get_student_by_id_number(student_id_number)

    if not student:
        raise StudentNotFoundError(student_id_number)

    return student


@router.get(
    "/search/",
    response_model=PaginatedResponse,
    summary="Пошук студентів",
    description="Пошук студентів за різними критеріями"
)
@limiter.limit(f"{RATE_LIMIT_REQUESTS}/{RATE_LIMIT_PERIOD}")
async def search_students(
    request: Request,
    query: str = Query(None, description="Пошуковий запит (прізвище, email, група)"),
    group_name: str = Query(None, description="Фільтр за назвою групи"),
    specialty_code: str = Query(None, description="Фільтр за кодом спеціальності"),
    course_number: int = Query(None, ge=1, le=6, description="Фільтр за номером курсу"),
    offset: int = Query(0, ge=0, description="Зміщення"),
    limit: int = Query(50, ge=1, le=100, description="Кількість записів")
):
    """
    Пошук студентів за критеріями.

    Args:
        query: Загальний пошук (last_name, email, group_name)
        group_name: Точний фільтр за групою
        specialty_code: Фільтр за кодом спеціальності
        course_number: Фільтр за курсом
        offset: Зміщення
        limit: Кількість

    Returns:
        PaginatedResponse: Результати пошуку
    """
    search_params = {
        'offset': offset,
        'limit': limit
    }

    if query:
        search_params['query'] = query
    if group_name:
        search_params['group_name'] = group_name
    if specialty_code:
        search_params['specialty_code'] = specialty_code
    if course_number:
        search_params['course_number'] = course_number

    students, total = service.search_students(search_params)

    return PaginatedResponse(
        total=total,
        offset=offset,
        limit=limit,
        items=[s.to_dict() for s in students]
    )


@router.put(
    "/{student_id_number}",
    response_model=StudentFullInfoResponse,
    summary="Оновити студента",
    description="Оновити дані студента за номером залікової книжки (часткове оновлення - вказуйте тільки поля які потрібно змінити)"
)
@limiter.limit(f"{RATE_LIMIT_REQUESTS_CREATE}/{RATE_LIMIT_PERIOD_CREATE}")
async def update_student(request: Request, student_id_number: str, student_data: StudentUpdate):
    """
    Оновити студента за номером залікової книжки.

    Args:
        student_id_number: Номер залікової книжки студента
        student_data: Дані для оновлення (всі поля опціональні - вказуйте тільки ті що змінюються)

    Returns:
        StudentFullInfoResponse: Оновлений студент

    Raises:
        404: Студент не знайдений
        422: Невалідні дані
        409: Конфлікт (дублікат номера залікової)
    """
    # Convert to dict and filter out unset values (only include fields that were provided)
    data = student_data.model_dump(exclude_unset=True)

    if not data:
        # No fields to update - just return current student
        student = service.get_student_by_id_number(student_id_number)
        if not student:
            raise StudentNotFoundError(student_id_number)
        return student

    # Update
    success = service.update_student_by_id_number(student_id_number, data)

    if not success:
        raise StudentNotFoundError(student_id_number)

    # Get updated student
    student = service.get_student_by_id_number(student_id_number)

    return student


@router.delete(
    "/{student_id_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити студента",
    description="Видалити студента за номером залікової книжки"
)
@limiter.limit(f"{RATE_LIMIT_REQUESTS_CREATE}/{RATE_LIMIT_PERIOD_CREATE}")
async def delete_student(request: Request, student_id_number: str):
    """
    Видалити студента за номером залікової книжки.

    Args:
        student_id_number: Номер залікової книжки студента

    Raises:
        404: Студент не знайдений
    """
    success = service.delete_student_by_id_number(student_id_number)

    if not success:
        raise StudentNotFoundError(student_id_number)


@router.get(
    "/export/json",
    summary="Експорт у JSON",
    description="Експортувати студентів у JSON файл з можливістю фільтрації",
    response_class=FileResponse
)
@limiter.limit(f"{RATE_LIMIT_REQUESTS_CREATE}/{RATE_LIMIT_PERIOD_CREATE}")
async def export_json(
    request: Request,
    query: str = Query(None, description="Пошуковий запит (прізвище, email, група)"),
    group_name: str = Query(None, description="Фільтр за назвою групи"),
    specialty_code: str = Query(None, description="Фільтр за кодом спеціальності"),
    course_number: int = Query(None, ge=1, le=6, description="Фільтр за номером курсу")
):
    """
    Експортувати студентів у JSON з фільтрацією.

    Args:
        query: Загальний пошук (last_name, email, group_name)
        group_name: Точний фільтр за групою
        specialty_code: Фільтр за кодом спеціальності
        course_number: Фільтр за курсом

    Returns:
        FileResponse: JSON файл для завантаження
    """
    # Build search parameters
    search_params = {}
    if query:
        search_params['query'] = query
    if group_name:
        search_params['group_name'] = group_name
    if specialty_code:
        search_params['specialty_code'] = specialty_code
    if course_number:
        search_params['course_number'] = course_number

    # Create temp file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.json')
    os.close(temp_fd)

    try:
        # Export with filters
        count = service.export_to_json(temp_path, search_params=search_params if search_params else None)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'students_{timestamp}.json'

        return FileResponse(
            path=temp_path,
            media_type='application/json',
            filename=filename,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'X-Total-Count': str(count)
            }
        )
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e


@router.get(
    "/export/csv",
    summary="Експорт у CSV",
    description="Експортувати студентів у CSV файл з можливістю фільтрації",
    response_class=FileResponse
)
@limiter.limit(f"{RATE_LIMIT_REQUESTS_CREATE}/{RATE_LIMIT_PERIOD_CREATE}")
async def export_csv(
    request: Request,
    query: str = Query(None, description="Пошуковий запит (прізвище, email, група)"),
    group_name: str = Query(None, description="Фільтр за назвою групи"),
    specialty_code: str = Query(None, description="Фільтр за кодом спеціальності"),
    course_number: int = Query(None, ge=1, le=6, description="Фільтр за номером курсу")
):
    """
    Експортувати студентів у CSV з фільтрацією.

    Args:
        query: Загальний пошук (last_name, email, group_name)
        group_name: Точний фільтр за групою
        specialty_code: Фільтр за кодом спеціальності
        course_number: Фільтр за курсом

    Returns:
        FileResponse: CSV файл для завантаження
    """
    # Build search parameters
    search_params = {}
    if query:
        search_params['query'] = query
    if group_name:
        search_params['group_name'] = group_name
    if specialty_code:
        search_params['specialty_code'] = specialty_code
    if course_number:
        search_params['course_number'] = course_number

    # Create temp file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.csv')
    os.close(temp_fd)

    try:
        # Export with filters
        count = service.export_to_csv(temp_path, search_params=search_params if search_params else None)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'students_{timestamp}.csv'

        return FileResponse(
            path=temp_path,
            media_type='text/csv; charset=utf-8',
            filename=filename,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'X-Total-Count': str(count)
            }
        )
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e
