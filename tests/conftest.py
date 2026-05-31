"""
Pytest конфігурація та fixtures.

Fixtures для тестування всіх компонентів системи.
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import date, timedelta
from typing import Generator, Dict, Any

from fastapi.testclient import TestClient

from src.repositories import StudentRepository
from src.services import StudentService
from src.api.main import app


# ==========================================
# Database Fixtures
# ==========================================

@pytest.fixture(scope="session")
def test_db_connection():
    """
    Тестове підключення до БД.

    Використовує ту ж БД що і основний додаток.
    Для ізоляції тестів використовуємо транзакції або окрему тестову БД.
    """
    from src.repositories.database import DatabaseConnection

    db = DatabaseConnection()

    # Перевірити підключення
    if not db.test_connection():
        pytest.skip("Database connection failed")

    yield db

    # Cleanup після всіх тестів
    db.close()


@pytest.fixture
def student_repository(test_db_connection):
    """Fixture для StudentRepository."""
    return StudentRepository()


@pytest.fixture
def student_service(student_repository):
    """Fixture для StudentService."""
    return StudentService(student_repository=student_repository)


# ==========================================
# API Fixtures
# ==========================================

@pytest.fixture
def api_client() -> TestClient:
    """
    Fixture для FastAPI TestClient.

    Returns:
        TestClient для тестування API endpoints
    """
    return TestClient(app)


# ==========================================
# Test Data Fixtures
# ==========================================

@pytest.fixture
def sample_group_data() -> Dict[str, Any]:
    """Приклад даних групи для тестів."""
    return {
        'id': 1,
        'name': 'CS-11',
        'specialty_id': 1,
        'course_id': 1,
        'admission_year': 2024
    }


@pytest.fixture
def sample_student_data() -> Dict[str, Any]:
    """
    Приклад валідних даних студента для тестів.

    Returns:
        Словник з валідними даними студента
    """
    return {
        'last_name': 'Shevchenko',
        'first_name': 'Taras',
        'patronymic': 'Hryhorovych',
        'student_id_number': 'TS-2024',
        'group_id': 1,
        'email': 'taras.shevchenko@example.com',
        'phone': '+380501234567',
        'birth_date': date(2005, 3, 9),
        'enrollment_date': date(2024, 9, 1)
    }


@pytest.fixture
def sample_student_data_minimal() -> Dict[str, Any]:
    """
    Мінімальні обов'язкові дані студента.

    Returns:
        Словник з мінімальними даними
    """
    return {
        'last_name': 'Franko',
        'first_name': 'Ivan',
        'patronymic': 'Yakovych',
        'student_id_number': 'IF-2025',
        'group_id': 1,
        'email': 'ivan.franko@example.com',
        'birth_date': date(2006, 8, 27)
    }


@pytest.fixture
def invalid_student_data() -> Dict[str, Any]:
    """
    Невалідні дані студента для тестування валідації.

    Returns:
        Словник з невалідними даними
    """
    return {
        'last_name': '',  # Empty
        'first_name': 'Test',
        'student_id_number': 'INVALID',  # Wrong format
        'group_id': 999999,  # Non-existent
        'email': 'not-an-email',  # Invalid email
        'phone': '123',  # Invalid phone
        'birth_date': date(1900, 1, 1)  # Too old
    }


@pytest.fixture
def multiple_students_data() -> list[Dict[str, Any]]:
    """
    Список з декількома студентами для тестів.

    Returns:
        Список словників з даними студентів
    """
    return [
        {
            'last_name': 'Ukrainka',
            'first_name': 'Lesya',
            'patronymic': 'Petrivna',
            'student_id_number': 'LU-2024',
            'group_id': 1,
            'email': 'lesya.ukrainka@example.com',
            'phone': '+380671234567',
            'birth_date': date(2005, 2, 25),
        },
        {
            'last_name': 'Kotsiubynsky',
            'first_name': 'Mykhailo',
            'patronymic': 'Mykhailovych',
            'student_id_number': 'MK-2024',
            'group_id': 1,
            'email': 'mykhailo.kotsiubynsky@example.com',
            'phone': '+380931234567',
            'birth_date': date(2006, 9, 17),
        },
        {
            'last_name': 'Lesia',
            'first_name': 'Olena',
            'patronymic': 'Ivanivna',
            'student_id_number': 'OL-2024',
            'group_id': 1,
            'email': 'olena.lesia@example.com',
            'birth_date': date(2005, 12, 5),
        }
    ]


# ==========================================
# File Fixtures
# ==========================================

@pytest.fixture
def temp_file() -> Generator[str, None, None]:
    """
    Тимчасовий файл для тестів експорту/імпорту.

    Yields:
        Шлях до тимчасового файлу
    """
    # Створити тимчасовий файл
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)

    yield path

    # Видалити після тесту
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_json_file() -> Generator[str, None, None]:
    """Тимчасовий JSON файл."""
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_csv_file() -> Generator[str, None, None]:
    """Тимчасовий CSV файл."""
    fd, path = tempfile.mkstemp(suffix='.csv')
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    """
    Тимчасова директорія для тестів.

    Yields:
        Path до тимчасової директорії
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# ==========================================
# Cleanup Fixtures
# ==========================================

@pytest.fixture
def cleanup_test_students(student_repository):
    """
    Fixture для очищення тестових студентів після тесту.

    Зберігає ID створених студентів і видаляє їх після тесту.
    """
    created_ids = []

    def register_student(student_id: int):
        """Зареєструвати студента для очищення."""
        created_ids.append(student_id)

    yield register_student

    # Очистити після тесту
    for student_id in created_ids:
        try:
            student_repository.delete(student_id)
        except Exception:
            pass  # Ігнорувати помилки при очищенні


# ==========================================
# Helper Functions
# ==========================================

@pytest.fixture
def assert_student_data():
    """
    Helper fixture для перевірки даних студента.

    Returns:
        Функція для перевірки
    """
    def _assert(actual: Dict[str, Any], expected: Dict[str, Any], skip_fields: list = None):
        """
        Порівняти дані студента.

        Args:
            actual: Фактичні дані
            expected: Очікувані дані
            skip_fields: Поля що пропускаються (наприклад, 'id', 'enrollment_date')
        """
        skip_fields = skip_fields or ['id', 'enrollment_date']

        for key, value in expected.items():
            if key in skip_fields:
                continue

            assert key in actual, f"Field '{key}' not found in actual data"

            # Порівняти значення
            if isinstance(value, date):
                actual_date = actual[key]
                if isinstance(actual_date, str):
                    actual_date = date.fromisoformat(actual_date)
                assert actual_date == value, f"Date mismatch for '{key}': {actual_date} != {value}"
            else:
                assert actual[key] == value, f"Value mismatch for '{key}': {actual[key]} != {value}"

    return _assert


# ==========================================
# Database State Fixtures
# ==========================================

@pytest.fixture
def ensure_test_group_exists(student_repository):
    """
    Переконатися що тестова група існує в БД.

    Yields:
        ID тестової групи
    """
    groups = student_repository.get_all_groups()

    if not groups:
        pytest.skip("No groups available in database. Run init.sql first.")

    # Повернути ID першої групи
    yield groups[0]['id']


@pytest.fixture
def database_statistics(student_repository):
    """
    Отримати статистику БД до та після тесту.

    Yields:
        Словник зі статистикою
    """
    stats_before = {
        'total_students': student_repository.count(),
        'total_groups': len(student_repository.get_all_groups()),
    }

    yield stats_before

    stats_after = {
        'total_students': student_repository.count(),
        'total_groups': len(student_repository.get_all_groups()),
    }

    # Логування змін
    students_diff = stats_after['total_students'] - stats_before['total_students']
    if students_diff != 0:
        print(f"\n[DB Change] Students: {students_diff:+d}")


# ==========================================
# Pytest Configuration
# ==========================================

def pytest_configure(config):
    """Конфігурація pytest."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires database)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API test"
    )
