"""
Тести для бізнес-логіки (Services).

Тестування StudentService з валідацією.
"""

import pytest
from datetime import date

from src.services import StudentService
from src.utils import ValidationError


@pytest.mark.integration
class TestStudentService:
    """Тести для StudentService."""

    def test_service_initialization(self, student_service):
        """Тест ініціалізації сервісу."""
        assert student_service is not None
        assert hasattr(student_service, 'create_student')
        assert hasattr(student_service, 'get_student')

    def test_create_student_valid_data(self, student_service, sample_student_data, cleanup_test_students):
        """Тест створення студента з валідними даними."""
        student_id = student_service.create_student(sample_student_data)
        cleanup_test_students(student_id)

        assert isinstance(student_id, int)
        assert student_id > 0

    def test_create_student_minimal_data(self, student_service, sample_student_data_minimal, cleanup_test_students):
        """Тест створення студента з мінімальними даними."""
        student_id = student_service.create_student(sample_student_data_minimal)
        cleanup_test_students(student_id)

        assert isinstance(student_id, int)

        # Перевірити що студент створено
        student = student_service.get_student(student_id)
        assert student is not None
        assert student.last_name == sample_student_data_minimal['last_name']

    def test_create_student_invalid_email(self, student_service, sample_student_data):
        """Тест створення студента з невалідним email."""
        invalid_data = sample_student_data.copy()
        invalid_data['email'] = 'not-an-email'

        with pytest.raises(ValidationError):
            student_service.create_student(invalid_data)

    def test_create_student_invalid_phone(self, student_service, sample_student_data):
        """Тест створення студента з невалідним телефоном."""
        invalid_data = sample_student_data.copy()
        invalid_data['phone'] = '123'

        with pytest.raises(ValidationError):
            student_service.create_student(invalid_data)

    def test_create_student_invalid_birth_date(self, student_service, sample_student_data):
        """Тест створення студента з невалідною датою народження."""
        invalid_data = sample_student_data.copy()
        invalid_data['birth_date'] = date(1900, 1, 1)  # Занадто старий

        with pytest.raises(ValidationError):
            student_service.create_student(invalid_data)

    def test_create_student_duplicate_student_id(self, student_service, sample_student_data, cleanup_test_students):
        """Тест створення студента з дублікатом номера залікової."""
        # Створити першого студента
        student_id1 = student_service.create_student(sample_student_data)
        cleanup_test_students(student_id1)

        # Спробувати створити другого з тим же номером
        duplicate_data = sample_student_data.copy()
        duplicate_data['email'] = 'different@example.com'

        with pytest.raises(ValueError, match="already exists"):
            student_service.create_student(duplicate_data)

    def test_get_student_existing(self, student_service, sample_student_data, cleanup_test_students):
        """Тест отримання існуючого студента."""
        student_id = student_service.create_student(sample_student_data)
        cleanup_test_students(student_id)

        student = student_service.get_student(student_id)

        assert student is not None
        assert student.id == student_id
        assert student.last_name == sample_student_data['last_name']
        assert student.email == sample_student_data['email']

    def test_get_student_non_existing(self, student_service):
        """Тест отримання неіснуючого студента."""
        with pytest.raises(ValueError, match="does not exist"):
            student_service.get_student(999999)

    def test_list_students(self, student_service):
        """Тест отримання списку студентів."""
        students, total = student_service.list_students(offset=0, limit=10)

        assert isinstance(students, list)
        assert isinstance(total, int)
        assert len(students) <= 10

    def test_list_students_pagination(self, student_service):
        """Тест пагінації списку студентів."""
        # Перша сторінка
        page1, total = student_service.list_students(offset=0, limit=5)

        assert len(page1) <= 5

        # Друга сторінка (якщо є достатньо студентів)
        if total > 5:
            page2, _ = student_service.list_students(offset=5, limit=5)
            assert len(page2) <= 5

            # Студенти не повинні повторюватися
            if page1 and page2:
                ids1 = {s.id for s in page1}
                ids2 = {s.id for s in page2}
                assert not ids1.intersection(ids2)

    def test_search_students(self, student_service, sample_student_data, cleanup_test_students):
        """Тест пошуку студентів."""
        student_id = student_service.create_student(sample_student_data)
        cleanup_test_students(student_id)

        # Пошук за прізвищем
        results, count = student_service.search_students({
            'query': sample_student_data['last_name']
        })

        assert count > 0
        assert any(s.id == student_id for s in results)

    def test_search_students_by_email(self, student_service, sample_student_data, cleanup_test_students):
        """Тест пошуку за email."""
        student_id = student_service.create_student(sample_student_data)
        cleanup_test_students(student_id)

        results, count = student_service.search_students({
            'query': sample_student_data['email']
        })

        assert count > 0
        found = any(s.id == student_id for s in results)
        assert found

    def test_update_student(self, student_service, sample_student_data, cleanup_test_students):
        """Тест оновлення студента."""
        student_id = student_service.create_student(sample_student_data)
        cleanup_test_students(student_id)

        # Оновити email
        new_email = "updated@example.com"
        updated = student_service.update_student(student_id, {'email': new_email})

        assert updated is True

        # Перевірити що оновилося
        student = student_service.get_student(student_id)
        assert student.email == new_email

    def test_update_student_invalid_email(self, student_service, sample_student_data, cleanup_test_students):
        """Тест оновлення з невалідним email."""
        student_id = student_service.create_student(sample_student_data)
        cleanup_test_students(student_id)

        with pytest.raises(ValidationError):
            student_service.update_student(student_id, {'email': 'not-an-email'})

    def test_update_non_existing_student(self, student_service):
        """Тест оновлення неіснуючого студента."""
        with pytest.raises(ValueError, match="does not exist"):
            student_service.update_student(999999, {'email': 'test@example.com'})

    def test_delete_student(self, student_service, sample_student_data):
        """Тест видалення студента."""
        student_id = student_service.create_student(sample_student_data)

        # Видалити
        deleted = student_service.delete_student(student_id)
        assert deleted is True

        # Перевірити що видалено
        with pytest.raises(ValueError, match="does not exist"):
            student_service.get_student(student_id)

    def test_delete_non_existing_student(self, student_service):
        """Тест видалення неіснуючого студента."""
        with pytest.raises(ValueError, match="does not exist"):
            student_service.delete_student(999999)

    def test_get_groups(self, student_service):
        """Тест отримання списку груп."""
        groups = student_service.get_groups()

        assert isinstance(groups, list)
        assert len(groups) > 0

        first_group = groups[0]
        assert 'id' in first_group
        assert 'name' in first_group

    def test_get_specialties(self, student_service):
        """Тест отримання списку спеціальностей."""
        specialties = student_service.get_specialties()

        assert isinstance(specialties, list)
        assert len(specialties) > 0

        first_specialty = specialties[0]
        assert 'id' in first_specialty
        assert 'name' in first_specialty
        assert 'code' in first_specialty

    def test_get_courses(self, student_service):
        """Тест отримання списку курсів."""
        courses = student_service.get_courses()

        assert isinstance(courses, list)
        assert len(courses) == 6  # Має бути 6 курсів

        # Перевірити що курси від 1 до 6
        course_numbers = [c['course_number'] for c in courses]
        assert sorted(course_numbers) == [1, 2, 3, 4, 5, 6]

    def test_export_to_json(self, student_service, temp_json_file):
        """Тест експорту в JSON."""
        count = student_service.export_to_json(temp_json_file)

        assert isinstance(count, int)
        assert count >= 0

        # Перевірити що файл створено
        import os
        assert os.path.exists(temp_json_file)

    def test_export_to_csv(self, student_service, temp_csv_file):
        """Тест експорту в CSV."""
        count = student_service.export_to_csv(temp_csv_file)

        assert isinstance(count, int)
        assert count >= 0

        # Перевірити що файл створено
        import os
        assert os.path.exists(temp_csv_file)

    def test_get_statistics(self, student_service):
        """Тест отримання статистики."""
        stats = student_service.get_statistics()

        assert isinstance(stats, dict)
        assert 'total_students' in stats
        assert 'total_groups' in stats
        assert 'total_specialties' in stats
        assert 'total_courses' in stats
        assert 'students_by_course' in stats

        assert isinstance(stats['total_students'], int)
        assert isinstance(stats['students_by_course'], list)

    def test_student_exists(self, student_service, sample_student_data, cleanup_test_students):
        """Тест перевірки існування студента."""
        student_id = student_service.create_student(sample_student_data)
        cleanup_test_students(student_id)

        assert student_service.student_exists(student_id) is True
        assert student_service.student_exists(999999) is False
