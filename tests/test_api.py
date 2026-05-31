"""
Тести для REST API endpoints.

Integration тести для FastAPI додатку.
"""

import pytest
from datetime import date


@pytest.mark.api
@pytest.mark.integration
class TestHealthEndpoint:
    """Тести для health check endpoint."""

    def test_health_check(self, api_client):
        """Тест health check endpoint."""
        response = api_client.get("/health")

        assert response.status_code == 200

        data = response.json()
        assert 'status' in data
        assert data['status'] in ['ok', 'healthy']


@pytest.mark.api
@pytest.mark.integration
class TestStudentsEndpoints:
    """Тести для /api/students endpoints."""

    def test_create_student(self, api_client, sample_student_data):
        """Тест створення студента через API."""
        # Конвертувати дати в рядки для JSON
        payload = sample_student_data.copy()
        payload['birth_date'] = payload['birth_date'].isoformat()
        if 'enrollment_date' in payload:
            payload['enrollment_date'] = payload['enrollment_date'].isoformat()

        response = api_client.post("/api/students/", json=payload)

        assert response.status_code == 201

        data = response.json()
        assert 'id' in data
        assert isinstance(data['id'], int)

        # Cleanup: видалити створеного студента
        student_id = data['id']
        api_client.delete(f"/api/students/{student_id}")

    def test_create_student_invalid_email(self, api_client, sample_student_data):
        """Тест створення з невалідним email."""
        payload = sample_student_data.copy()
        payload['email'] = 'not-an-email'
        payload['birth_date'] = payload['birth_date'].isoformat()

        response = api_client.post("/api/students/", json=payload)

        assert response.status_code == 422  # Validation Error

    def test_create_student_missing_required_field(self, api_client):
        """Тест створення без обов'язкового поля."""
        payload = {
            'first_name': 'Test',
            'email': 'test@example.com',
            'birth_date': '2005-01-01'
            # Відсутнє last_name
        }

        response = api_client.post("/api/students/", json=payload)

        assert response.status_code == 422

    def test_get_students_list(self, api_client):
        """Тест отримання списку студентів."""
        response = api_client.get("/api/students/")

        assert response.status_code == 200

        data = response.json()
        assert 'students' in data
        assert 'total' in data
        assert isinstance(data['students'], list)
        assert isinstance(data['total'], int)

    def test_get_students_pagination(self, api_client):
        """Тест пагінації списку студентів."""
        response = api_client.get("/api/students/?offset=0&limit=5")

        assert response.status_code == 200

        data = response.json()
        assert len(data['students']) <= 5

    def test_get_student_by_id(self, api_client, sample_student_data):
        """Тест отримання студента за ID."""
        # Створити студента
        payload = sample_student_data.copy()
        payload['birth_date'] = payload['birth_date'].isoformat()
        create_response = api_client.post("/api/students/", json=payload)
        student_id = create_response.json()['id']

        # Отримати студента
        response = api_client.get(f"/api/students/{student_id}")

        assert response.status_code == 200

        data = response.json()
        assert data['id'] == student_id
        assert data['last_name'] == sample_student_data['last_name']

        # Cleanup
        api_client.delete(f"/api/students/{student_id}")

    def test_get_student_non_existing(self, api_client):
        """Тест отримання неіснуючого студента."""
        response = api_client.get("/api/students/999999")

        assert response.status_code == 404

    def test_search_students(self, api_client, sample_student_data):
        """Тест пошуку студентів."""
        # Створити студента
        payload = sample_student_data.copy()
        payload['birth_date'] = payload['birth_date'].isoformat()
        create_response = api_client.post("/api/students/", json=payload)
        student_id = create_response.json()['id']

        # Пошук
        response = api_client.get(
            f"/api/students/search/?query={sample_student_data['last_name']}"
        )

        assert response.status_code == 200

        data = response.json()
        assert 'students' in data
        assert 'total' in data
        assert data['total'] > 0

        # Cleanup
        api_client.delete(f"/api/students/{student_id}")

    def test_update_student(self, api_client, sample_student_data):
        """Тест оновлення студента."""
        # Створити студента
        payload = sample_student_data.copy()
        payload['birth_date'] = payload['birth_date'].isoformat()
        create_response = api_client.post("/api/students/", json=payload)
        student_id = create_response.json()['id']

        # Оновити
        update_payload = {'email': 'newemail@example.com'}
        response = api_client.put(f"/api/students/{student_id}", json=update_payload)

        assert response.status_code == 200

        data = response.json()
        assert data['success'] is True

        # Перевірити що оновилося
        get_response = api_client.get(f"/api/students/{student_id}")
        assert get_response.json()['email'] == 'newemail@example.com'

        # Cleanup
        api_client.delete(f"/api/students/{student_id}")

    def test_update_student_invalid_data(self, api_client, sample_student_data):
        """Тест оновлення з невалідними даними."""
        # Створити студента
        payload = sample_student_data.copy()
        payload['birth_date'] = payload['birth_date'].isoformat()
        create_response = api_client.post("/api/students/", json=payload)
        student_id = create_response.json()['id']

        # Спробувати оновити з невалідним email
        update_payload = {'email': 'not-an-email'}
        response = api_client.put(f"/api/students/{student_id}", json=update_payload)

        assert response.status_code == 422

        # Cleanup
        api_client.delete(f"/api/students/{student_id}")

    def test_delete_student(self, api_client, sample_student_data):
        """Тест видалення студента."""
        # Створити студента
        payload = sample_student_data.copy()
        payload['birth_date'] = payload['birth_date'].isoformat()
        create_response = api_client.post("/api/students/", json=payload)
        student_id = create_response.json()['id']

        # Видалити
        response = api_client.delete(f"/api/students/{student_id}")

        assert response.status_code == 204

        # Перевірити що видалено
        get_response = api_client.get(f"/api/students/{student_id}")
        assert get_response.status_code == 404

    def test_delete_non_existing_student(self, api_client):
        """Тест видалення неіснуючого студента."""
        response = api_client.delete("/api/students/999999")

        assert response.status_code == 404

    def test_export_json(self, api_client):
        """Тест експорту в JSON."""
        response = api_client.get("/api/students/export/json")

        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/json'

        # Має бути attachment
        assert 'attachment' in response.headers.get('content-disposition', '')

    def test_export_csv(self, api_client):
        """Тест експорту в CSV."""
        response = api_client.get("/api/students/export/csv")

        assert response.status_code == 200
        assert 'text/csv' in response.headers['content-type']

        # Має бути attachment
        assert 'attachment' in response.headers.get('content-disposition', '')


@pytest.mark.api
@pytest.mark.integration
class TestReferenceEndpoints:
    """Тести для /api/reference endpoints."""

    def test_get_groups(self, api_client):
        """Тест отримання списку груп."""
        response = api_client.get("/api/reference/groups")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        first_group = data[0]
        assert 'id' in first_group
        assert 'name' in first_group

    def test_get_specialties(self, api_client):
        """Тест отримання списку спеціальностей."""
        response = api_client.get("/api/reference/specialties")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        first_specialty = data[0]
        assert 'id' in first_specialty
        assert 'name' in first_specialty
        assert 'code' in first_specialty

    def test_get_courses(self, api_client):
        """Тест отримання списку курсів."""
        response = api_client.get("/api/reference/courses")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 6  # Має бути 6 курсів

        # Перевірити структуру
        first_course = data[0]
        assert 'id' in first_course
        assert 'course_number' in first_course
        assert 'name' in first_course


@pytest.mark.api
class TestAPIDocumentation:
    """Тести для автоматичної документації API."""

    def test_swagger_ui_available(self, api_client):
        """Тест доступності Swagger UI."""
        response = api_client.get("/docs")

        assert response.status_code == 200
        assert 'text/html' in response.headers['content-type']

    def test_redoc_available(self, api_client):
        """Тест доступності ReDoc."""
        response = api_client.get("/redoc")

        assert response.status_code == 200
        assert 'text/html' in response.headers['content-type']

    def test_openapi_schema(self, api_client):
        """Тест OpenAPI схеми."""
        response = api_client.get("/openapi.json")

        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/json'

        schema = response.json()
        assert 'openapi' in schema
        assert 'paths' in schema
        assert 'components' in schema


@pytest.mark.api
class TestCORS:
    """Тести для CORS middleware."""

    def test_cors_headers_present(self, api_client):
        """Тест наявності CORS заголовків."""
        response = api_client.options("/api/students/")

        # Перевірити наявність CORS заголовків
        assert 'access-control-allow-origin' in response.headers
        assert 'access-control-allow-methods' in response.headers
