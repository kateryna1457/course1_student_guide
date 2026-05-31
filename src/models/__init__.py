"""
Модуль моделей даних.

Експортує всі OOP класи та Pydantic схеми.
"""

from .course import Course
from .specialty import Specialty
from .group import Group
from .student import Student, StudentFullInfo
from .schemas import (
    CourseResponse,
    SpecialtyResponse,
    GroupResponse,
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentFullInfoResponse,
    StudentSearchParams,
    PaginatedResponse
)

__all__ = [
    # OOP Models
    "Course",
    "Specialty",
    "Group",
    "Student",
    "StudentFullInfo",
    # Pydantic Schemas
    "CourseResponse",
    "SpecialtyResponse",
    "GroupResponse",
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    "StudentFullInfoResponse",
    "StudentSearchParams",
    "PaginatedResponse"
]
