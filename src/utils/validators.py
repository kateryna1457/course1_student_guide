import re
from datetime import date, datetime
from typing import Optional

from src.constants import (
    MIN_STUDENT_AGE,
    MAX_STUDENT_AGE,
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH,
    MIN_EMAIL_LENGTH,
    MAX_EMAIL_LENGTH,
    MIN_STUDENT_ID_LENGTH,
    MAX_STUDENT_ID_LENGTH,
    MIN_GROUP_NAME_LENGTH,
    MAX_GROUP_NAME_LENGTH,
    MIN_SPECIALTY_CODE_LENGTH,
    MAX_SPECIALTY_CODE_LENGTH,
    MIN_COURSE_NUMBER,
    MAX_COURSE_NUMBER,
    MIN_ADMISSION_YEAR,
)


class ValidationError(Exception):
    """Виняток для помилок валідації."""
    pass


def validate_student_id_number(student_id: str) -> bool:
    """
    Валідація номера залікової книжки.

    Формати, що підтримуються:
    - XX-NNNN (наприклад, CS-2024, SE-0001)
    - XXNNNN (наприклад, CS2024)
    - XXX-NNNN (наприклад, CSC-2024)

    Args:
        student_id: Номер залікової книжки

    Returns:
        bool: True якщо формат правильний

    Raises:
        ValidationError: Якщо формат неправильний
    """
    if not student_id or not isinstance(student_id, str):
        raise ValidationError("Student ID number is required and must be a string")

    student_id = student_id.strip()

    if len(student_id) < MIN_STUDENT_ID_LENGTH:
        raise ValidationError(f"Student ID number must be at least {MIN_STUDENT_ID_LENGTH} characters long")

    if len(student_id) > MAX_STUDENT_ID_LENGTH:
        raise ValidationError(f"Student ID number must not exceed {MAX_STUDENT_ID_LENGTH} characters")

    pattern = r'^[A-Z]{2,4}-?\d{1,6}$'

    if not re.match(pattern, student_id, re.IGNORECASE):
        raise ValidationError(
            "Student ID number must match format: XX-NNNN or XXNNNN "
            "(letters followed by optional dash and numbers)"
        )

    return True


def validate_group_name(group_name: str) -> bool:
    """
    Валідація назви групи.

    Очікуваний формат: XX-NN (наприклад, CS-11, SE-21, IT-31)

    Args:
        group_name: Назва групи

    Returns:
        bool: True якщо формат правильний

    Raises:
        ValidationError: Якщо формат неправильний
    """
    if not group_name or not isinstance(group_name, str):
        raise ValidationError("Group name is required and must be a string")

    group_name = group_name.strip()

    if len(group_name) < MIN_GROUP_NAME_LENGTH:
        raise ValidationError(f"Group name must be at least {MIN_GROUP_NAME_LENGTH} characters long")

    if len(group_name) > MAX_GROUP_NAME_LENGTH:
        raise ValidationError(f"Group name must not exceed {MAX_GROUP_NAME_LENGTH} characters")

    pattern = r'^[A-Z]{2,4}-\d{1,2}$'

    if not re.match(pattern, group_name, re.IGNORECASE):
        raise ValidationError(
            "Group name must match format: XX-NN "
            "(2-4 letters, dash, 1-2 digits, e.g., CS-11)"
        )

    return True


def validate_course_number(course_number: int) -> bool:
    """
    Валідація номера курсу.

    Args:
        course_number: Номер курсу (1-6)

    Returns:
        bool: True якщо курс в діапазоні 1-6

    Raises:
        ValidationError: Якщо курс поза діапазоном
    """
    if not isinstance(course_number, int):
        raise ValidationError("Course number must be an integer")

    if not (MIN_COURSE_NUMBER <= course_number <= MAX_COURSE_NUMBER):
        raise ValidationError(f"Course number must be between {MIN_COURSE_NUMBER} and {MAX_COURSE_NUMBER}, got {course_number}")

    return True


def validate_email(email: str) -> bool:
    """
    Валідація електронної пошти.

    Args:
        email: Електронна адреса

    Returns:
        bool: True якщо email правильний

    Raises:
        ValidationError: Якщо email неправильний
    """
    if not email or not isinstance(email, str):
        raise ValidationError("Email is required and must be a string")

    email = email.strip().lower()

    if len(email) < MIN_EMAIL_LENGTH:
        raise ValidationError(f"Email is too short (min {MIN_EMAIL_LENGTH} characters)")

    if len(email) > MAX_EMAIL_LENGTH:
        raise ValidationError(f"Email is too long (max {MAX_EMAIL_LENGTH} characters)")

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")

    return True


def validate_phone(phone: str) -> bool:
    """
    Валідація номера телефону (український формат).

    Підтримувані формати:
    - +380XXXXXXXXX (міжнародний формат)
    - 0XXXXXXXXX (національний формат)
    - (0XX) XXX-XX-XX
    - 0XX-XXX-XX-XX

    Args:
        phone: Номер телефону

    Returns:
        bool: True якщо телефон правильний

    Raises:
        ValidationError: Якщо телефон неправильний
    """
    if not phone or not isinstance(phone, str):
        raise ValidationError("Phone number is required and must be a string")

    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)

    patterns = [
        r'^\+380\d{9}$',  # +380XXXXXXXXX
        r'^380\d{9}$',    # 380XXXXXXXXX
        r'^0\d{9}$',      # 0XXXXXXXXX
    ]

    if not any(re.match(pattern, cleaned_phone) for pattern in patterns):
        raise ValidationError(
            "Invalid phone number format. "
            "Expected formats: +380XXXXXXXXX, 0XXXXXXXXX"
        )

    return True


def validate_birth_date(birth_date: date, min_age: int = MIN_STUDENT_AGE, max_age: int = MAX_STUDENT_AGE) -> bool:
    """
    Валідація дати народження.

    Перевіряє чи вік студента в допустимому діапазоні.

    Args:
        birth_date: Дата народження
        min_age: Мінімальний вік (за замовчуванням 15)
        max_age: Максимальний вік (за замовчуванням 100)

    Returns:
        bool: True якщо дата правильна

    Raises:
        ValidationError: Якщо дата неправильна
    """
    if not birth_date:
        raise ValidationError("Birth date is required")

    if not isinstance(birth_date, date):
        raise ValidationError("Birth date must be a date object")

    today = date.today()

    if birth_date > today:
        raise ValidationError("Birth date cannot be in the future")

    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    if age < min_age:
        raise ValidationError(f"Student must be at least {min_age} years old (current age: {age})")

    if age > max_age:
        raise ValidationError(f"Invalid birth date (age cannot exceed {max_age} years)")

    return True


def validate_admission_year(admission_year: int) -> bool:
    """
    Валідація року вступу.

    Args:
        admission_year: Рік вступу

    Returns:
        bool: True якщо рік правильний

    Raises:
        ValidationError: Якщо рік неправильний
    """
    if not isinstance(admission_year, int):
        raise ValidationError("Admission year must be an integer")

    current_year = datetime.now().year

    if not (MIN_ADMISSION_YEAR <= admission_year <= current_year + 1):
        raise ValidationError(
            f"Admission year must be between {MIN_ADMISSION_YEAR} and {current_year + 1}, got {admission_year}"
        )

    return True


def validate_specialty_code(code: str) -> bool:
    """
    Валідація коду спеціальності.

    Args:
        code: Код спеціальності (наприклад, '121', '122', '122-DS')

    Returns:
        bool: True якщо код правильний

    Raises:
        ValidationError: Якщо код неправильний
    """
    if not code or not isinstance(code, str):
        raise ValidationError("Specialty code is required and must be a string")

    code = code.strip()

    if len(code) < MIN_SPECIALTY_CODE_LENGTH:
        raise ValidationError(f"Specialty code must be at least {MIN_SPECIALTY_CODE_LENGTH} characters long")

    if len(code) > MAX_SPECIALTY_CODE_LENGTH:
        raise ValidationError(f"Specialty code must not exceed {MAX_SPECIALTY_CODE_LENGTH} characters")

    pattern = r'^\d{3}(-[A-Z]{1,4})?$'

    if not re.match(pattern, code, re.IGNORECASE):
        raise ValidationError(
            "Specialty code must match format: NNN or NNN-XX "
            "(3 digits optionally followed by dash and 1-4 letters)"
        )

    return True


def validate_not_empty(value: Optional[str], field_name: str) -> bool:
    """
    Перевірка що поле не порожнє.

    Args:
        value: Значення для перевірки
        field_name: Назва поля (для повідомлення про помилку)

    Returns:
        bool: True якщо значення не порожнє

    Raises:
        ValidationError: Якщо значення порожнє
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"{field_name} cannot be empty")

    return True


def validate_string_length(
    value: str,
    field_name: str,
    min_length: int = MIN_NAME_LENGTH,
    max_length: int = MAX_NAME_LENGTH
) -> bool:
    """
    Валідація довжини рядка.

    Args:
        value: Рядок для перевірки
        field_name: Назва поля
        min_length: Мінімальна довжина
        max_length: Максимальна довжина

    Returns:
        bool: True якщо довжина правильна

    Raises:
        ValidationError: Якщо довжина неправильна
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")

    length = len(value.strip())

    if length < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters long (got {length})"
        )

    if length > max_length:
        raise ValidationError(
            f"{field_name} must not exceed {max_length} characters (got {length})"
        )

    return True


def validate_student_data(
    last_name: str,
    first_name: str,
    student_id_number: str,
    email: str,
    birth_date: date,
    patronymic: Optional[str] = None,
    phone: Optional[str] = None
) -> bool:
    """
    Комплексна валідація даних студента.

    Args:
        last_name: Прізвище
        first_name: Ім'я
        student_id_number: Номер залікової книжки
        email: Email
        birth_date: Дата народження
        patronymic: По батькові (опціонально)
        phone: Телефон (опціонально)

    Returns:
        bool: True якщо всі дані правильні

    Raises:
        ValidationError: Якщо будь-які дані неправильні
    """
    validate_string_length(last_name, "Last name", MIN_NAME_LENGTH, MAX_NAME_LENGTH)
    validate_string_length(first_name, "First name", MIN_NAME_LENGTH, MAX_NAME_LENGTH)
    validate_student_id_number(student_id_number)
    validate_email(email)
    validate_birth_date(birth_date)

    if patronymic:
        validate_string_length(patronymic, "Patronymic", MIN_NAME_LENGTH, MAX_NAME_LENGTH)

    if phone:
        validate_phone(phone)

    return True
