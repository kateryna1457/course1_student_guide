"""
Тести для репозиторіїв.

Integration тести для PostgreSQL репозиторію.
"""

import pytest
from datetime import date

from src.repositories import StudentRepository
from src.utils import ValidationError


@pytest.mark.integration
class TestStudentRepository:
    """Integration тести для StudentRepository."""

    def test_repository_initialization(self, student_repository):
        """Тест ініціалізації репозиторію."""
        assert student_repository is not None
        assert hasattr(student_repository, 'create')
        assert hasattr(student_repository, 'get_by_id')
        assert hasattr(student_repository, 'get_all')

    def test_get_all_groups(self, student_repository):
        """Тест отримання всіх груп."""
        groups = student_repository.get_all_groups()

        assert isinstance(groups, list)
        assert len(groups) > 0, "Should have groups from init.sql"

        # Перевірити структуру першої групи
        first_group = groups[0]
        assert 'id' in first_group
        assert 'name' in first_group
        assert 'admission_year' in first_group

    def test_get_all_specialties(self, student_repository):
        """Тест отримання всіх спеціальностей."""
        specialties = student_repository.get_all_specialties()

        assert isinstance(specialties, list)
        assert len(specialties) > 0, "Should have specialties from init.sql"

        first_specialty = specialties[0]
        assert 'id' in first_specialty
        assert 'name' in first_specialty
        assert 'code' in first_specialty

    def test_get_all_courses(self, student_repository):
        """Тест отримання всіх курсів."""
        courses = student_repository.get_all_courses()

        assert isinstance(courses, list)
        assert len(courses) == 6, "Should have 6 courses (1-6)"

        # Перевірити що курси від 1 до 6
        course_numbers = [c['course_number'] for c in courses]
        assert sorted(course_numbers) == [1, 2, 3, 4, 5, 6]

    def test_create_student(self, student_repository, sample_student_data, cleanup_test_students):
        """Тест створення студента."""
        # Створити студента
        student_id = student_repository.create(sample_student_data)
        cleanup_test_students(student_id)

        assert isinstance(student_id, int)
        assert student_id > 0

    def test_get_by_id_existing(self, student_repository, sample_student_data, cleanup_test_students):
        """Тест отримання студента за ID (існуючого)."""
        # Створити студента
        student_id = student_repository.create(sample_student_data)
        cleanup_test_students(student_id)

        # Отримати студента
        student = student_repository.get_by_id(student_id)

        assert student is not None
        assert student.id == student_id
        assert student.last_name == sample_student_data['last_name']
        assert student.first_name == sample_student_data['first_name']
        assert student.email == sample_student_data['email']

    def test_get_by_id_non_existing(self, student_repository):
        """Тест отримання неіснуючого студента."""
        # Використати ID що напевно не існує
        non_existing_id = 999999

        student = student_repository.get_by_id(non_existing_id)
        assert student is None

    def test_get_all_pagination(self, student_repository):
        """Тест пагінації при отриманні всіх студентів."""
        # Отримати першу сторінку
        students_page1, total = student_repository.get_all(offset=0, limit=5)

        assert isinstance(students_page1, list)
        assert isinstance(total, int)
        assert len(students_page1) <= 5

        # Якщо є студенти, перевірити другу сторінку
        if total > 5:
            students_page2, _ = student_repository.get_all(offset=5, limit=5)
            assert len(students_page2) <= 5

            # Студенти на різних сторінках не повинні перетинатися
            if students_page1 and students_page2:
                ids_page1 = {s.id for s in students_page1}
                ids_page2 = {s.id for s in students_page2}
                assert not ids_page1.intersection(ids_page2)

    def test_search_by_last_name(self, student_repository, sample_student_data, cleanup_test_students):
        """Тест пошуку за прізвищем."""
        # Створити студента
        student_id = student_repository.create(sample_student_data)
        cleanup_test_students(student_id)

        # Пошук
        results, count = student_repository.search({
            'query': sample_student_data['last_name']
        })

        assert count > 0
        assert any(s.id == student_id for s in results)

    def test_search_by_email(self, student_repository, sample_student_data, cleanup_test_students):
        """Тест пошуку за email."""
        student_id = student_repository.create(sample_student_data)
        cleanup_test_students(student_id)

        results, count = student_repository.search({
            'query': sample_student_data['email']
        })

        assert count > 0
        assert any(s.id == student_id for s in results)

    def test_update_student(self, student_repository, sample_student_data, cleanup_test_students):
        """Тест оновлення студента."""
        # Створити студента
        student_id = student_repository.create(sample_student_data)
        cleanup_test_students(student_id)

        # Оновити email
        new_email = "newemail@example.com"
        updated = student_repository.update(student_id, {'email': new_email})

        assert updated is True

        # Перевірити що оновилося
        student = student_repository.get_by_id(student_id)
        assert student.email == new_email

    def test_delete_student(self, student_repository, sample_student_data):
        """Тест видалення студента."""
        # Створити студента
        student_id = student_repository.create(sample_student_data)

        # Видалити
        deleted = student_repository.delete(student_id)
        assert deleted is True

        # Перевірити що видалено
        student = student_repository.get_by_id(student_id)
        assert student is None

    def test_exists_existing_student(self, student_repository, sample_student_data, cleanup_test_students):
        """Тест перевірки існування студента."""
        student_id = student_repository.create(sample_student_data)
        cleanup_test_students(student_id)

        assert student_repository.exists(student_id) is True

    def test_exists_non_existing_student(self, student_repository):
        """Тест перевірки неіснуючого студента."""
        assert student_repository.exists(999999) is False

    def test_exists_student_id_number(self, student_repository, sample_student_data, cleanup_test_students):
        """Тест перевірки існування номера залікової."""
        student_id = student_repository.create(sample_student_data)
        cleanup_test_students(student_id)

        exists = student_repository.exists_by_student_id_number(
            sample_student_data['student_id_number']
        )
        assert exists is True

    def test_count_students(self, student_repository):
        """Тест підрахунку студентів."""
        count = student_repository.count()
        assert isinstance(count, int)
        assert count >= 0

    def test_count_by_course(self, student_repository):
        """Тест підрахунку студентів по курсах."""
        courses = student_repository.get_all_courses()

        for course in courses:
            count = student_repository.count_by_course(course['id'])
            assert isinstance(count, int)
            assert count >= 0

    def test_duplicate_student_id_number(self, student_repository, sample_student_data, cleanup_test_students):
        """Тест що не можна створити дублікат номера залікової."""
        # Створити першого студента
        student_id1 = student_repository.create(sample_student_data)
        cleanup_test_students(student_id1)

        # Спробувати створити другого з тим же номером
        duplicate_data = sample_student_data.copy()
        duplicate_data['email'] = 'different@example.com'  # Інший email

        # Має викинути помилку (через UNIQUE constraint)
        with pytest.raises(Exception):  # PostgresError або IntegrityError
            student_repository.create(duplicate_data)


@pytest.mark.integration
class TestExportRepository:
    """Тести для ExportRepository."""

    def test_export_to_json(self, temp_json_file):
        """Тест експорту в JSON."""
        from src.repositories import ExportRepository

        export_repo = ExportRepository()
        count = export_repo.export_to_json(temp_json_file)

        assert isinstance(count, int)
        assert count >= 0

        # Перевірити що файл створено
        import os
        assert os.path.exists(temp_json_file)
        assert os.path.getsize(temp_json_file) > 0

    def test_export_to_csv(self, temp_csv_file):
        """Тест експорту в CSV."""
        from src.repositories import ExportRepository

        export_repo = ExportRepository()
        count = export_repo.export_to_csv(temp_csv_file)

        assert isinstance(count, int)
        assert count >= 0

        # Перевірити що файл створено
        import os
        assert os.path.exists(temp_csv_file)
        assert os.path.getsize(temp_csv_file) > 0

    def test_json_file_structure(self, temp_json_file):
        """Тест структури JSON файлу."""
        from src.repositories import ExportRepository
        import json

        export_repo = ExportRepository()
        export_repo.export_to_json(temp_json_file)

        # Прочитати і перевірити структуру
        with open(temp_json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert isinstance(data, list)

        if data:  # Якщо є студенти
            first_student = data[0]
            assert 'id' in first_student
            assert 'last_name' in first_student
            assert 'email' in first_student

    def test_csv_file_structure(self, temp_csv_file):
        """Тест структури CSV файлу."""
        from src.repositories import ExportRepository
        import csv

        export_repo = ExportRepository()
        count = export_repo.export_to_csv(temp_csv_file)

        if count > 0:
            # Прочитати і перевірити структуру
            with open(temp_csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                assert len(rows) == count

                if rows:
                    first_row = rows[0]
                    assert 'id' in first_row
                    assert 'last_name' in first_row
                    assert 'email' in first_row
