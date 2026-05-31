"""
Тести для OOP моделей.

Тестування класів Student, Group, Specialty, Course.
"""

import pytest
from datetime import date

from src.models import Student, StudentFullInfo, Group, Specialty, Course


class TestStudent:
    """Тести для моделі Student."""

    def test_student_creation(self):
        """Тест створення студента."""
        student = Student(
            id=1,
            last_name="Shevchenko",
            first_name="Taras",
            patronymic="Hryhorovych",
            student_id_number="TS-2024",
            group_id=1,
            email="taras@example.com",
            phone="+380501234567",
            birth_date=date(2005, 3, 9),
            enrollment_date=date(2024, 9, 1)
        )

        assert student.id == 1
        assert student.last_name == "Shevchenko"
        assert student.first_name == "Taras"
        assert student.patronymic == "Hryhorovych"
        assert student.student_id_number == "TS-2024"
        assert student.email == "taras@example.com"

    def test_student_without_optional_fields(self):
        """Тест створення студента без опціональних полів."""
        student = Student(
            id=2,
            last_name="Franko",
            first_name="Ivan",
            patronymic=None,
            student_id_number="IF-2024",
            group_id=1,
            email="ivan@example.com",
            phone=None,
            birth_date=date(2005, 8, 27),
            enrollment_date=date(2024, 9, 1)
        )

        assert student.patronymic is None
        assert student.phone is None

    def test_student_get_full_name_with_patronymic(self):
        """Тест отримання повного ПІБ з по батькові."""
        student = Student(
            id=1,
            last_name="Shevchenko",
            first_name="Taras",
            patronymic="Hryhorovych",
            student_id_number="TS-2024",
            group_id=1,
            email="taras@example.com",
            birth_date=date(2005, 3, 9),
            enrollment_date=date(2024, 9, 1)
        )

        assert student.get_full_name() == "Shevchenko Taras Hryhorovych"

    def test_student_get_full_name_without_patronymic(self):
        """Тест отримання повного імені без по батькові."""
        student = Student(
            id=2,
            last_name="Franko",
            first_name="Ivan",
            patronymic=None,
            student_id_number="IF-2024",
            group_id=1,
            email="ivan@example.com",
            birth_date=date(2005, 8, 27),
            enrollment_date=date(2024, 9, 1)
        )

        assert student.get_full_name() == "Franko Ivan"

    def test_student_to_dict(self):
        """Тест конвертації студента в словник."""
        student = Student(
            id=1,
            last_name="Shevchenko",
            first_name="Taras",
            patronymic="Hryhorovych",
            student_id_number="TS-2024",
            group_id=1,
            email="taras@example.com",
            phone="+380501234567",
            birth_date=date(2005, 3, 9),
            enrollment_date=date(2024, 9, 1)
        )

        student_dict = student.to_dict()

        assert isinstance(student_dict, dict)
        assert student_dict['id'] == 1
        assert student_dict['last_name'] == "Shevchenko"
        assert student_dict['first_name'] == "Taras"
        assert student_dict['email'] == "taras@example.com"


class TestStudentFullInfo:
    """Тести для моделі StudentFullInfo."""

    def test_student_full_info_creation(self):
        """Тест створення StudentFullInfo з повною інформацією."""
        student = StudentFullInfo(
            id=1,
            last_name="Shevchenko",
            first_name="Taras",
            patronymic="Hryhorovych",
            student_id_number="TS-2024",
            email="taras@example.com",
            phone="+380501234567",
            birth_date=date(2005, 3, 9),
            enrollment_date=date(2024, 9, 1),
            group_name="CS-11",
            admission_year=2024,
            course_number=1,
            course_name="First Year",
            specialty_name="Computer Science",
            specialty_code="121"
        )

        assert student.id == 1
        assert student.group_name == "CS-11"
        assert student.course_number == 1
        assert student.specialty_name == "Computer Science"
        assert student.specialty_code == "121"
        assert student.admission_year == 2024

    def test_student_full_info_inheritance(self):
        """Тест що StudentFullInfo успадковує Student."""
        student = StudentFullInfo(
            id=1,
            last_name="Shevchenko",
            first_name="Taras",
            patronymic="Hryhorovych",
            student_id_number="TS-2024",
            email="taras@example.com",
            birth_date=date(2005, 3, 9),
            enrollment_date=date(2024, 9, 1),
            group_name="CS-11",
            admission_year=2024,
            course_number=1,
            course_name="First Year",
            specialty_name="Computer Science",
            specialty_code="121"
        )

        # Має методи базового Student
        assert hasattr(student, 'get_full_name')
        assert student.get_full_name() == "Shevchenko Taras Hryhorovych"


class TestGroup:
    """Тести для моделі Group."""

    def test_group_creation(self):
        """Тест створення групи."""
        group = Group(
            id=1,
            name="CS-11",
            specialty_id=1,
            course_id=1,
            admission_year=2024
        )

        assert group.id == 1
        assert group.name == "CS-11"
        assert group.specialty_id == 1
        assert group.course_id == 1
        assert group.admission_year == 2024

    def test_group_to_dict(self):
        """Тест конвертації групи в словник."""
        group = Group(
            id=1,
            name="CS-11",
            specialty_id=1,
            course_id=1,
            admission_year=2024
        )

        group_dict = group.to_dict()

        assert isinstance(group_dict, dict)
        assert group_dict['id'] == 1
        assert group_dict['name'] == "CS-11"
        assert group_dict['admission_year'] == 2024


class TestSpecialty:
    """Тести для моделі Specialty."""

    def test_specialty_creation_full(self):
        """Тест створення спеціальності з усіма полями."""
        specialty = Specialty(
            id=1,
            name="Computer Science",
            code="121",
            description="Study of computation and information"
        )

        assert specialty.id == 1
        assert specialty.name == "Computer Science"
        assert specialty.code == "121"
        assert specialty.description == "Study of computation and information"

    def test_specialty_creation_minimal(self):
        """Тест створення спеціальності з мінімальними полями."""
        specialty = Specialty(
            id=2,
            name="Software Engineering",
            code="122",
            description=None
        )

        assert specialty.id == 2
        assert specialty.name == "Software Engineering"
        assert specialty.description is None

    def test_specialty_to_dict(self):
        """Тест конвертації спеціальності в словник."""
        specialty = Specialty(
            id=1,
            name="Computer Science",
            code="121",
            description="Study of computation"
        )

        specialty_dict = specialty.to_dict()

        assert isinstance(specialty_dict, dict)
        assert specialty_dict['name'] == "Computer Science"
        assert specialty_dict['code'] == "121"


class TestCourse:
    """Тести для моделі Course."""

    def test_course_creation(self):
        """Тест створення курсу."""
        course = Course(
            id=1,
            course_number=1,
            name="First Year"
        )

        assert course.id == 1
        assert course.course_number == 1
        assert course.name == "First Year"

    def test_course_number_range(self):
        """Тест різних номерів курсів (1-6)."""
        for i in range(1, 7):
            course = Course(
                id=i,
                course_number=i,
                name=f"Year {i}"
            )
            assert course.course_number == i

    def test_course_to_dict(self):
        """Тест конвертації курсу в словник."""
        course = Course(
            id=1,
            course_number=1,
            name="First Year"
        )

        course_dict = course.to_dict()

        assert isinstance(course_dict, dict)
        assert course_dict['course_number'] == 1
        assert course_dict['name'] == "First Year"
