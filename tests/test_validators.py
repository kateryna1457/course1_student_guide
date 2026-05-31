"""
Тести для валідаторів.

Тестування функцій валідації даних студентів.
"""

import pytest
from datetime import date, timedelta

from src.utils.validators import (
    ValidationError,
    validate_student_id_number,
    validate_group_name,
    validate_course_number,
    validate_email,
    validate_phone,
    validate_birth_date,
    validate_admission_year,
    validate_specialty_code,
    validate_not_empty,
    validate_string_length,
    validate_student_data
)


class TestValidateStudentIdNumber:
    """Тести для validate_student_id_number."""

    def test_valid_student_id_numbers(self):
        """Тест валідних номерів залікових книжок."""
        valid_ids = [
            "CS-1234",
            "IT-5678",
            "SE-9999",
            "AB-0001",
            "XY-4567"
        ]

        for student_id in valid_ids:
            validate_student_id_number(student_id)  # Не має викидати помилку

    def test_invalid_format(self):
        """Тест невалідного формату."""
        invalid_ids = [
            "CS1234",      # Без дефісу
            "CS-123",      # 3 цифри замість 4
            "CS-12345",    # 5 цифр
            "C-1234",      # 1 літера
            "CSE-1234",    # 3 літери
            "12-1234",     # Цифри замість літер
            "",            # Пустий рядок
            "CS -1234",    # Пробіл
        ]

        for student_id in invalid_ids:
            with pytest.raises(ValidationError):
                validate_student_id_number(student_id)

    def test_case_sensitivity(self):
        """Тест чутливості до регістру."""
        # Uppercase має бути валідним
        validate_student_id_number("CS-1234")

        # Lowercase теж може бути валідним (залежить від вимог)
        # Якщо lowercase невалідний, розкоментувати:
        # with pytest.raises(ValidationError):
        #     validate_student_id_number("cs-1234")


class TestValidateGroupName:
    """Тести для validate_group_name."""

    def test_valid_group_names(self):
        """Тест валідних назв груп."""
        valid_groups = [
            "CS-11",
            "IT-23",
            "SE-56",
            "AB-12"
        ]

        for group_name in valid_groups:
            validate_group_name(group_name)

    def test_invalid_format(self):
        """Тест невалідного формату."""
        invalid_groups = [
            "CS11",        # Без дефісу
            "CS-1",        # 1 цифра
            "CS-123",      # 3 цифри
            "C-11",        # 1 літера
            "CSE-11",      # 3 літери
            "",            # Пустий
        ]

        for group_name in invalid_groups:
            with pytest.raises(ValidationError):
                validate_group_name(group_name)


class TestValidateCourseNumber:
    """Тести для validate_course_number."""

    def test_valid_course_numbers(self):
        """Тест валідних номерів курсів (1-6)."""
        for course in range(1, 7):
            validate_course_number(course)

    def test_invalid_course_numbers(self):
        """Тест невалідних номерів курсів."""
        invalid_courses = [0, -1, 7, 10, 100]

        for course in invalid_courses:
            with pytest.raises(ValidationError):
                validate_course_number(course)


class TestValidateEmail:
    """Тести для validate_email."""

    def test_valid_emails(self):
        """Тест валідних email адрес."""
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "student@university.edu.ua",
            "a@b.c",
        ]

        for email in valid_emails:
            validate_email(email)

    def test_invalid_emails(self):
        """Тест невалідних email адрес."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",  # Пробіл
            "",
            "user@.com",
            "user..name@example.com",
        ]

        for email in invalid_emails:
            with pytest.raises(ValidationError):
                validate_email(email)


class TestValidatePhone:
    """Тести для validate_phone."""

    def test_valid_ukrainian_phones(self):
        """Тест валідних українських номерів."""
        valid_phones = [
            "+380501234567",
            "+380671234567",
            "+380931234567",
            "+380991234567",
        ]

        for phone in valid_phones:
            validate_phone(phone)

    def test_invalid_phones(self):
        """Тест невалідних номерів."""
        invalid_phones = [
            "380501234567",    # Без +
            "+38050123456",    # 9 цифр
            "+3805012345678",  # 11 цифр
            "+380 50 123 45 67",  # З пробілами
            "+1234567890",     # Не український
            "",
            "123",
        ]

        for phone in invalid_phones:
            with pytest.raises(ValidationError):
                validate_phone(phone)


class TestValidateBirthDate:
    """Тести для validate_birth_date."""

    def test_valid_birth_dates(self):
        """Тест валідних дат народження."""
        today = date.today()

        valid_dates = [
            today - timedelta(days=365 * 18),  # 18 років
            today - timedelta(days=365 * 25),  # 25 років
            today - timedelta(days=365 * 50),  # 50 років
        ]

        for birth_date in valid_dates:
            validate_birth_date(birth_date)

    def test_too_young(self):
        """Тест дати народження - занадто молодий."""
        today = date.today()
        too_young = today - timedelta(days=365 * 10)  # 10 років

        with pytest.raises(ValidationError, match="not be younger than 15"):
            validate_birth_date(too_young)

    def test_too_old(self):
        """Тест дати народження - занадто старий."""
        too_old = date(1900, 1, 1)

        with pytest.raises(ValidationError, match="not be older than 100"):
            validate_birth_date(too_old)

    def test_future_date(self):
        """Тест майбутньої дати."""
        future = date.today() + timedelta(days=365)

        with pytest.raises(ValidationError, match="cannot be in the future"):
            validate_birth_date(future)


class TestValidateAdmissionYear:
    """Тести для validate_admission_year."""

    def test_valid_admission_years(self):
        """Тест валідних років вступу."""
        current_year = date.today().year

        valid_years = [
            current_year - 5,
            current_year - 1,
            current_year,
            current_year + 1,
        ]

        for year in valid_years:
            validate_admission_year(year)

    def test_too_old_year(self):
        """Тест занадто старого року."""
        old_year = 1990

        with pytest.raises(ValidationError):
            validate_admission_year(old_year)

    def test_too_future_year(self):
        """Тест занадто далекого майбутнього."""
        current_year = date.today().year
        future_year = current_year + 10

        with pytest.raises(ValidationError):
            validate_admission_year(future_year)


class TestValidateSpecialtyCode:
    """Тести для validate_specialty_code."""

    def test_valid_specialty_codes(self):
        """Тест валідних кодів спеціальностей."""
        valid_codes = [
            "121",
            "122",
            "123",
            "124",
            "125",
            "126",
        ]

        for code in valid_codes:
            validate_specialty_code(code)

    def test_invalid_codes(self):
        """Тест невалідних кодів."""
        invalid_codes = [
            "12",      # 2 цифри
            "1234",    # 4 цифри
            "ABC",     # Літери
            "",
        ]

        for code in invalid_codes:
            with pytest.raises(ValidationError):
                validate_specialty_code(code)


class TestValidateNotEmpty:
    """Тести для validate_not_empty."""

    def test_valid_non_empty_strings(self):
        """Тест непустих рядків."""
        valid_strings = [
            "Test",
            "Hello World",
            "  Test  ",  # З пробілами на початку/кінці
            "123",
        ]

        for value in valid_strings:
            validate_not_empty(value, "test_field")

    def test_empty_strings(self):
        """Тест пустих рядків."""
        invalid_values = [
            "",
            "   ",     # Тільки пробіли
            "\t",      # Тільки табуляція
            "\n",      # Тільки новий рядок
        ]

        for value in invalid_values:
            with pytest.raises(ValidationError):
                validate_not_empty(value, "test_field")


class TestValidateStringLength:
    """Тести для validate_string_length."""

    def test_valid_length(self):
        """Тест валідної довжини рядка."""
        validate_string_length("Test", "field", max_length=10)
        validate_string_length("Hello", "field", max_length=5)
        validate_string_length("A", "field", max_length=100)

    def test_too_long(self):
        """Тест занадто довгого рядка."""
        with pytest.raises(ValidationError):
            validate_string_length("Hello World", "field", max_length=5)

    def test_empty_allowed(self):
        """Тест що пустий рядок дозволений."""
        validate_string_length("", "field", max_length=10)


class TestValidateStudentData:
    """Тести для validate_student_data (комплексна валідація)."""

    def test_valid_student_data(self):
        """Тест валідних даних студента."""
        valid_data = {
            'last_name': 'Shevchenko',
            'first_name': 'Taras',
            'patronymic': 'Hryhorovych',
            'student_id_number': 'TS-2024',
            'email': 'taras@example.com',
            'phone': '+380501234567',
            'birth_date': date(2005, 3, 9)
        }

        # Не має викидати помилку
        validate_student_data(valid_data)

    def test_valid_student_data_minimal(self):
        """Тест мінімальних валідних даних."""
        minimal_data = {
            'last_name': 'Franko',
            'first_name': 'Ivan',
            'student_id_number': 'IF-2024',
            'email': 'ivan@example.com',
            'birth_date': date(2005, 8, 27)
        }

        validate_student_data(minimal_data)

    def test_invalid_last_name(self):
        """Тест невалідного прізвища."""
        data = {
            'last_name': '',  # Пусте
            'first_name': 'Taras',
            'student_id_number': 'TS-2024',
            'email': 'taras@example.com',
            'birth_date': date(2005, 3, 9)
        }

        with pytest.raises(ValidationError):
            validate_student_data(data)

    def test_invalid_email(self):
        """Тест невалідного email."""
        data = {
            'last_name': 'Shevchenko',
            'first_name': 'Taras',
            'student_id_number': 'TS-2024',
            'email': 'not-an-email',  # Невалідний
            'birth_date': date(2005, 3, 9)
        }

        with pytest.raises(ValidationError):
            validate_student_data(data)

    def test_invalid_phone(self):
        """Тест невалідного телефону."""
        data = {
            'last_name': 'Shevchenko',
            'first_name': 'Taras',
            'student_id_number': 'TS-2024',
            'email': 'taras@example.com',
            'phone': '123',  # Невалідний
            'birth_date': date(2005, 3, 9)
        }

        with pytest.raises(ValidationError):
            validate_student_data(data)

    def test_invalid_birth_date(self):
        """Тест невалідної дати народження."""
        data = {
            'last_name': 'Shevchenko',
            'first_name': 'Taras',
            'student_id_number': 'TS-2024',
            'email': 'taras@example.com',
            'birth_date': date(1900, 1, 1)  # Занадто старий
        }

        with pytest.raises(ValidationError):
            validate_student_data(data)

    def test_none_values_for_optional_fields(self):
        """Тест None для опціональних полів."""
        data = {
            'last_name': 'Franko',
            'first_name': 'Ivan',
            'patronymic': None,  # Опціональний
            'student_id_number': 'IF-2024',
            'email': 'ivan@example.com',
            'phone': None,  # Опціональний
            'birth_date': date(2005, 8, 27)
        }

        validate_student_data(data)
