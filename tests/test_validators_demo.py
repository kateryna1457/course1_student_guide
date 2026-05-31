"""
Демонстраційні тести валідаторів.

Цей файл показує як працюють валідатори.
"""

from datetime import date
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.validators import (
    ValidationError,
    validate_student_id_number,
    validate_group_name,
    validate_course_number,
    validate_email,
    validate_phone,
    validate_birth_date,
    validate_specialty_code,
    validate_student_data
)


def test_validator(name: str, func, *args, **kwargs):
    """Helper function to test validators."""
    try:
        result = func(*args, **kwargs)
        print(f"✓ {name}: PASSED")
        return True
    except ValidationError as e:
        print(f"✗ {name}: FAILED - {e}")
        return False
    except Exception as e:
        print(f"✗ {name}: ERROR - {e}")
        return False


def main():
    """Run validator tests."""
    print("=" * 60)
    print("VALIDATOR TESTS")
    print("=" * 60)
    print()

    # Student ID Number
    print("1. Student ID Number Validation:")
    test_validator("Valid: CS-2024", validate_student_id_number, "CS-2024")
    test_validator("Valid: SE2024", validate_student_id_number, "SE2024")
    test_validator("Valid: CSC-001", validate_student_id_number, "CSC-001")
    test_validator("Invalid: 123", validate_student_id_number, "123")
    test_validator("Invalid: CS", validate_student_id_number, "CS")
    print()

    # Group Name
    print("2. Group Name Validation:")
    test_validator("Valid: CS-11", validate_group_name, "CS-11")
    test_validator("Valid: SE-21", validate_group_name, "SE-21")
    test_validator("Valid: CSCI-1", validate_group_name, "CSCI-1")
    test_validator("Invalid: CS11", validate_group_name, "CS11")
    test_validator("Invalid: C-1", validate_group_name, "C-1")
    print()

    # Course Number
    print("3. Course Number Validation:")
    test_validator("Valid: 1", validate_course_number, 1)
    test_validator("Valid: 6", validate_course_number, 6)
    test_validator("Invalid: 0", validate_course_number, 0)
    test_validator("Invalid: 7", validate_course_number, 7)
    print()

    # Email
    print("4. Email Validation:")
    test_validator("Valid: student@example.com", validate_email, "student@example.com")
    test_validator("Valid: john.doe@university.edu.ua", validate_email, "john.doe@university.edu.ua")
    test_validator("Invalid: notanemail", validate_email, "notanemail")
    test_validator("Invalid: @example.com", validate_email, "@example.com")
    print()

    # Phone
    print("5. Phone Validation:")
    test_validator("Valid: +380501234567", validate_phone, "+380501234567")
    test_validator("Valid: 0501234567", validate_phone, "0501234567")
    test_validator("Valid: (050) 123-45-67", validate_phone, "(050) 123-45-67")
    test_validator("Invalid: 123", validate_phone, "123")
    test_validator("Invalid: +1234567890", validate_phone, "+1234567890")
    print()

    # Birth Date
    print("6. Birth Date Validation:")
    test_validator("Valid: 2000-01-01", validate_birth_date, date(2000, 1, 1))
    test_validator("Valid: 1990-06-15", validate_birth_date, date(1990, 6, 15))
    test_validator("Invalid: Too young", validate_birth_date, date.today())
    test_validator("Invalid: Future", validate_birth_date, date(2030, 1, 1))
    print()

    # Specialty Code
    print("7. Specialty Code Validation:")
    test_validator("Valid: 121", validate_specialty_code, "121")
    test_validator("Valid: 122-DS", validate_specialty_code, "122-DS")
    test_validator("Invalid: 12", validate_specialty_code, "12")
    test_validator("Invalid: ABC", validate_specialty_code, "ABC")
    print()

    # Complete Student Data
    print("8. Complete Student Data Validation:")
    test_validator(
        "Valid student data",
        validate_student_data,
        last_name="Shevchenko",
        first_name="Taras",
        student_id_number="CS-2024",
        email="shevchenko@example.com",
        birth_date=date(2000, 1, 1),
        patronymic="Hryhorovych",
        phone="+380501234567"
    )
    print()

    print("=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
