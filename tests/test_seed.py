"""
Тести для генератора тестових даних (seed).

Тестування DataGenerator та seed функцій.
"""

import pytest
from datetime import date

from src.utils.seed import DataGenerator, seed_database
from src.utils import validate_student_id_number, validate_email, validate_phone, validate_birth_date, ValidationError


class TestDataGenerator:
    """Тести для класу DataGenerator."""

    def test_generator_initialization(self):
        """Тест ініціалізації генератора."""
        generator = DataGenerator()

        assert generator is not None
        assert hasattr(generator, 'generate_student')
        assert hasattr(generator, 'generate_phone_number')

    def test_generate_student_id_number(self):
        """Тест генерації номера залікової книжки."""
        generator = DataGenerator()

        group_name = "CS-11"
        year = 2024

        student_id = generator.generate_student_id_number(group_name, year)

        assert isinstance(student_id, str)
        assert len(student_id) > 0

        # Перевірити формат через валідатор
        validate_student_id_number(student_id)

    def test_generate_phone_number(self):
        """Тест генерації телефонного номера."""
        generator = DataGenerator()

        phone = generator.generate_phone_number()

        assert isinstance(phone, str)
        assert phone.startswith('+380')

        # Перевірити через валідатор
        validate_phone(phone)

    def test_generate_birth_date(self):
        """Тест генерації дати народження."""
        generator = DataGenerator()

        birth_date = generator.generate_birth_date()

        assert isinstance(birth_date, date)

        # Перевірити через валідатор (вік 17-25 років)
        validate_birth_date(birth_date)

    def test_generate_birth_date_age_range(self):
        """Тест що генеровані дати в правильному діапазоні віку."""
        generator = DataGenerator()
        today = date.today()

        # Згенерувати 10 дат і перевірити вік
        for _ in range(10):
            birth_date = generator.generate_birth_date()

            age = today.year - birth_date.year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1

            assert 17 <= age <= 25, f"Age {age} is outside range 17-25"

    def test_generate_enrollment_date(self):
        """Тест генерації дати зарахування."""
        generator = DataGenerator()

        birth_date = date(2005, 3, 9)
        admission_year = 2024

        enrollment_date = generator.generate_enrollment_date(birth_date, admission_year)

        assert isinstance(enrollment_date, date)
        assert enrollment_date.year == admission_year
        # Має бути приблизно 1 вересня ± 10 днів
        assert 8 <= enrollment_date.month <= 9

    @pytest.mark.integration
    def test_generate_student(self, sample_group_data):
        """Тест генерації повних даних студента."""
        generator = DataGenerator()

        student = generator.generate_student(sample_group_data)

        assert isinstance(student, dict)

        # Перевірити обов'язкові поля
        required_fields = [
            'last_name', 'first_name', 'patronymic',
            'student_id_number', 'group_id', 'email',
            'birth_date', 'enrollment_date'
        ]

        for field in required_fields:
            assert field in student, f"Missing required field: {field}"
            if field not in ['phone', 'patronymic']:  # Опціональні
                assert student[field] is not None

        # Перевірити group_id
        assert student['group_id'] == sample_group_data['id']

    @pytest.mark.integration
    def test_generate_student_unique_ids(self, sample_group_data):
        """Тест що генеруються унікальні номери залікових."""
        generator = DataGenerator()

        # Згенерувати 10 студентів
        students = [generator.generate_student(sample_group_data) for _ in range(10)]

        # Зібрати всі student_id_number
        student_ids = [s['student_id_number'] for s in students]

        # Перевірити унікальність
        assert len(student_ids) == len(set(student_ids)), "Student ID numbers are not unique"

    @pytest.mark.integration
    def test_generated_data_validation(self, sample_group_data):
        """Тест що згенеровані дані проходять валідацію."""
        generator = DataGenerator()

        # Згенерувати 5 студентів
        for _ in range(5):
            student = generator.generate_student(sample_group_data)

            # Валідувати кожне поле
            validate_student_id_number(student['student_id_number'])
            validate_email(student['email'])

            if student.get('phone'):
                validate_phone(student['phone'])

            validate_birth_date(student['birth_date'])

    @pytest.mark.integration
    def test_get_statistics(self, student_repository):
        """Тест отримання статистики."""
        generator = DataGenerator(student_repository)

        stats = generator.get_statistics()

        assert isinstance(stats, dict)
        assert 'total_students' in stats
        assert 'total_groups' in stats
        assert 'total_specialties' in stats
        assert 'students_by_course' in stats


@pytest.mark.integration
@pytest.mark.slow
class TestSeedDatabase:
    """Integration тести для seed_database функції."""

    def test_seed_database_small_count(self, student_repository):
        """Тест seed з малою кількістю студентів."""
        initial_count = student_repository.count()

        # Seed 3 студентів
        created_count = seed_database(count=3)

        assert created_count == 3

        # Перевірити що студенти додалися
        final_count = student_repository.count()
        assert final_count == initial_count + 3

    def test_seed_database_no_groups_error(self):
        """Тест що seed викидає помилку якщо немає груп."""
        # Створити генератор з mock репозиторієм без груп
        from unittest.mock import Mock

        mock_repo = Mock()
        mock_repo.get_all_groups.return_value = []

        generator = DataGenerator(mock_repo)

        with pytest.raises(ValueError, match="Немає доступних груп"):
            generator.seed_students(count=5)


class TestDataQuality:
    """Тести якості згенерованих даних."""

    def test_email_transliteration(self):
        """Тест транслітерації українських символів в email."""
        generator = DataGenerator()

        # Тестова транслітерація (simplified check)
        # Реальна транслітерація відбувається в generate_student

        sample_group = {
            'id': 1,
            'name': 'CS-11',
            'admission_year': 2024
        }

        # Згенерувати кілька студентів і перевірити email
        for _ in range(5):
            student = generator.generate_student(sample_group)

            email = student['email']

            # Email не повинен містити кириличні символи
            # Перевірити що всі символи - ASCII
            try:
                email.encode('ascii')
            except UnicodeEncodeError:
                pytest.fail(f"Email contains non-ASCII characters: {email}")

    def test_phone_operator_codes(self):
        """Тест що використовуються правильні коди операторів."""
        generator = DataGenerator()

        valid_operators = ['50', '63', '66', '67', '68', '91', '92', '93', '94', '95', '96', '97', '98', '99']

        # Згенерувати 20 номерів
        phones = [generator.generate_phone_number() for _ in range(20)]

        for phone in phones:
            # Витягти код оператора
            operator_code = phone[4:6]  # +380XX...

            assert operator_code in valid_operators, f"Invalid operator code: {operator_code}"

    def test_gender_based_names(self):
        """Тест що імена правильно генеруються за родом."""
        # Цей тест складно зробити без знання конкретних імен
        # Але можна перевірити що ПІБ не пусті

        generator = DataGenerator()

        sample_group = {
            'id': 1,
            'name': 'CS-11',
            'admission_year': 2024
        }

        for _ in range(10):
            student = generator.generate_student(sample_group)

            assert len(student['last_name']) > 0
            assert len(student['first_name']) > 0
            assert len(student['patronymic']) > 0

    def test_phone_optional_80_percent(self):
        """Тест що ~80% студентів мають телефон."""
        generator = DataGenerator()

        sample_group = {
            'id': 1,
            'name': 'CS-11',
            'admission_year': 2024
        }

        # Згенерувати 100 студентів
        students = [generator.generate_student(sample_group) for _ in range(100)]

        # Підрахувати скільки мають телефон
        with_phone = sum(1 for s in students if s.get('phone') is not None)

        # Має бути приблизно 80% (±15% для статистичної варіації)
        percentage = (with_phone / 100) * 100
        assert 65 <= percentage <= 95, f"Phone percentage {percentage}% is outside expected range 65-95%"


class TestEdgeCases:
    """Тести граничних випадків."""

    def test_generate_with_very_long_group_name(self):
        """Тест генерації з довгою назвою групи."""
        generator = DataGenerator()

        long_group = {
            'id': 1,
            'name': 'VERYLONGPREFIX-11',
            'admission_year': 2024
        }

        student = generator.generate_student(long_group)

        assert student is not None
        assert 'student_id_number' in student

    def test_generate_multiple_same_group(self):
        """Тест генерації багатьох студентів в одній групі."""
        generator = DataGenerator()

        sample_group = {
            'id': 1,
            'name': 'CS-11',
            'admission_year': 2024
        }

        # Згенерувати 20 студентів в одній групі
        students = [generator.generate_student(sample_group) for _ in range(20)]

        assert len(students) == 20

        # Всі повинні бути в тій же групі
        for student in students:
            assert student['group_id'] == sample_group['id']
