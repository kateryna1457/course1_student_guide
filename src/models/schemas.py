from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, EmailStr, field_validator


# ==========================================
# Course Schemas
# ==========================================

class CourseResponse(BaseModel):
    """Схема відповіді для курсу."""

    id: int
    course_number: int = Field(..., ge=1, le=6, description="Номер курсу (1-6)")
    name: str = Field(..., min_length=1, max_length=100, description="Назва курсу")

    class Config:
        """Конфігурація Pydantic."""
        from_attributes = True


# ==========================================
# Specialty Schemas
# ==========================================

class SpecialtyResponse(BaseModel):
    """Схема відповіді для спеціальності."""

    id: int
    name: str = Field(..., min_length=1, max_length=200, description="Назва спеціальності")
    code: Optional[str] = Field(None, min_length=2, max_length=10, description="Код спеціальності")
    description: Optional[str] = Field(None, description="Опис спеціальності")

    class Config:
        """Конфігурація Pydantic."""
        from_attributes = True


# ==========================================
# Group Schemas
# ==========================================

class GroupResponse(BaseModel):
    """Схема відповіді для групи."""

    id: int
    name: str = Field(..., min_length=2, max_length=20, description="Назва групи")
    specialty_id: int = Field(..., description="ID спеціальності")
    course_id: int = Field(..., description="ID курсу")
    admission_year: int = Field(..., ge=1900, le=2100, description="Рік вступу")

    class Config:
        """Конфігурація Pydantic."""
        from_attributes = True


# ==========================================
# Student Schemas
# ==========================================

class StudentCreate(BaseModel):
    """Схема для створення студента."""

    last_name: str = Field(..., min_length=1, max_length=100, description="Прізвище")
    first_name: str = Field(..., min_length=1, max_length=100, description="Ім'я")
    patronymic: Optional[str] = Field(None, max_length=100, description="По батькові")
    student_id_number: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="Номер залікової книжки (унікальний, обов'язковий)"
    )
    group_id: int = Field(..., gt=0, description="ID групи")
    email: EmailStr = Field(..., description="Електронна пошта")
    phone: Optional[str] = Field(None, max_length=20, description="Номер телефону")
    birth_date: date = Field(..., description="Дата народження")

    @field_validator("student_id_number")
    @classmethod
    def validate_student_id_number(cls, v: str) -> str:
        """Валідація номера залікової книжки."""
        if not v or not v.strip():
            raise ValueError("Student ID number cannot be empty or whitespace")
        # Remove leading/trailing whitespace
        return v.strip()

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        """Валідація дати народження (мінімум 15 років)."""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 15:
            raise ValueError("Student must be at least 15 years old")
        if age > 100:
            raise ValueError("Invalid birth date")
        return v


class StudentUpdate(BaseModel):
    """Схема для оновлення студента (всі поля опціональні)."""

    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    patronymic: Optional[str] = Field(None, max_length=100)
    student_id_number: Optional[str] = Field(None, min_length=3, max_length=20, description="Номер залікової книжки (унікальний)")
    group_id: Optional[int] = Field(None, gt=0)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[date] = None

    @field_validator("student_id_number")
    @classmethod
    def validate_student_id_number(cls, v: Optional[str]) -> Optional[str]:
        """Валідація номера залікової книжки."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Student ID number cannot be empty or whitespace")
        # Remove leading/trailing whitespace
        return v.strip()

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        """Валідація дати народження."""
        if v is None:
            return v
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 15:
            raise ValueError("Student must be at least 15 years old")
        if age > 100:
            raise ValueError("Invalid birth date")
        return v


class StudentResponse(BaseModel):
    """Схема відповіді для студента (базова)."""

    id: int
    last_name: str
    first_name: str
    patronymic: Optional[str] = None
    student_id_number: str
    group_id: int
    email: str
    phone: Optional[str] = None
    birth_date: date
    enrollment_date: date

    class Config:
        """Конфігурація Pydantic."""
        from_attributes = True


class StudentFullInfoResponse(StudentResponse):
    """Схема відповіді з повною інформацією про студента (з JOIN)."""

    group_name: str = Field(..., description="Назва групи")
    admission_year: int = Field(..., description="Рік вступу групи")
    course_number: int = Field(..., description="Номер курсу")
    course_name: str = Field(..., description="Назва курсу")
    specialty_name: str = Field(..., description="Назва спеціальності")
    specialty_code: Optional[str] = Field(None, description="Код спеціальності")
    specialty_description: Optional[str] = Field(None, description="Опис спеціальності")

    class Config:
        """Конфігурація Pydantic."""
        from_attributes = True


# ==========================================
# Search & List Schemas
# ==========================================

class StudentSearchParams(BaseModel):
    """Параметри пошуку студентів."""

    query: Optional[str] = Field(None, description="Пошуковий запит (прізвище, email, група)")
    group_name: Optional[str] = Field(None, description="Фільтр за назвою групи")
    specialty_code: Optional[str] = Field(None, description="Фільтр за кодом спеціальності")
    course_number: Optional[int] = Field(None, ge=1, le=6, description="Фільтр за номером курсу")
    offset: int = Field(0, ge=0, description="Зміщення для пагінації")
    limit: int = Field(50, ge=1, le=100, description="Кількість записів")


class PaginatedResponse(BaseModel):
    """Схема для пагінованої відповіді."""

    total: int = Field(..., description="Загальна кількість записів")
    offset: int = Field(..., description="Зміщення")
    limit: int = Field(..., description="Ліміт")
    items: list = Field(..., description="Список елементів")


# ==========================================
# Error Schemas (hidden from docs)
# ==========================================

class ValidationError(BaseModel):
    """Схема помилки валідації."""

    detail: str
    error_type: str = "validation_error"

    model_config = {"json_schema_extra": {"exclude": True}}


class HTTPValidationError(BaseModel):
    """Схема помилки валідації HTTP."""

    detail: list
    error_type: str = "request_validation_error"

    model_config = {"json_schema_extra": {"exclude": True}}
