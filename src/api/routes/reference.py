"""
API роутер для довідкових даних (read-only).

Endpoints для отримання груп, спеціальностей, курсів.
"""

from typing import List
from fastapi import APIRouter

from src.models import GroupResponse, SpecialtyResponse, CourseResponse
from src.services import StudentService

# Створити router
router = APIRouter(prefix="/reference", tags=["reference"])

# Ініціалізувати сервіс
service = StudentService()


@router.get(
    "/groups",
    response_model=List[GroupResponse],
    summary="Список груп",
    description="Отримати список всіх груп (read-only)"
)
async def get_groups():
    """
    Отримати список всіх груп.

    Returns:
        List[GroupResponse]: Список груп
    """
    groups = service.get_groups()
    return groups


@router.get(
    "/specialties",
    response_model=List[SpecialtyResponse],
    summary="Список спеціальностей",
    description="Отримати список всіх спеціальностей (read-only)"
)
async def get_specialties():
    """
    Отримати список всіх спеціальностей.

    Returns:
        List[SpecialtyResponse]: Список спеціальностей
    """
    specialties = service.get_specialties()
    return specialties


@router.get(
    "/courses",
    response_model=List[CourseResponse],
    summary="Список курсів",
    description="Отримати список всіх курсів (read-only)"
)
async def get_courses():
    """
    Отримати список всіх курсів (1-6).

    Returns:
        List[CourseResponse]: Список курсів
    """
    courses = service.get_courses()
    return courses
