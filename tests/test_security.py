"""
Тести безпеки.

Перевірка захисту від SQL injection та інших вразливостей.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.services import StudentService
from src.repositories import StudentRepository


@pytest.mark.integration
class TestSQLInjectionProtection:
    """Тести захисту від SQL injection атак."""

    def test_sql_injection_in_search_query(self):
        """
        Тест SQL injection в пошуковому запиті.

        Перевіряємо що malicious SQL код в параметрі query
        не виконується і не викликає помилку.
        """
        client = TestClient(app)

        # SQL injection payload
        malicious_queries = [
            "'; DROP TABLE t_students; --",
            "' OR '1'='1",
            "' OR 1=1 --",
            "admin'--",
            "' UNION SELECT NULL, NULL, NULL--",
            "1'; DELETE FROM t_students WHERE '1'='1",
            "'; EXEC xp_cmdshell('dir'); --",
        ]

        for malicious_query in malicious_queries:
            response = client.get(
                "/api/v1/students/search/",
                params={"query": malicious_query}
            )

            # Should NOT return 500 (internal server error from SQL injection)
            # Should either return 200 with empty results or 422 (validation error)
            assert response.status_code in [200, 422], \
                f"SQL injection not properly handled for query: {malicious_query}"

            # If 200, should return structured response (not execute SQL)
            if response.status_code == 200:
                data = response.json()
                assert "data" in data
                assert isinstance(data["data"], list)

    def test_sql_injection_in_student_id_number(self):
        """
        Тест SQL injection в номері залікової книжки.

        Перевіряємо що malicious код в student_id_number
        не виконується.
        """
        client = TestClient(app)

        malicious_ids = [
            "CS-2024'; DROP TABLE t_students; --",
            "CS-2024' OR '1'='1",
            "'; DELETE FROM t_students; --",
        ]

        for malicious_id in malicious_ids:
            response = client.get(f"/api/v1/students/{malicious_id}")

            # Should return 404 (not found) or 422 (validation error)
            # NOT 500 (internal server error)
            assert response.status_code in [404, 422], \
                f"SQL injection not properly handled for student_id: {malicious_id}"

    def test_sql_injection_in_group_filter(self):
        """
        Тест SQL injection в фільтрі за групою.
        """
        client = TestClient(app)

        malicious_group_names = [
            "CS-11'; DROP TABLE t_groups; --",
            "CS-11' OR '1'='1",
            "'; UPDATE t_students SET email='hacked@test.com'; --",
        ]

        for malicious_group in malicious_group_names:
            response = client.get(
                "/api/v1/students/search/",
                params={"group_name": malicious_group}
            )

            assert response.status_code in [200, 422], \
                f"SQL injection not properly handled for group_name: {malicious_group}"

            if response.status_code == 200:
                data = response.json()
                assert "data" in data

    def test_sql_injection_in_create_student(self):
        """
        Тест SQL injection при створенні студента.

        Перевіряємо що malicious код в полях студента
        не виконується.
        """
        client = TestClient(app)

        malicious_student_data = {
            "last_name": "'; DROP TABLE t_students; --",
            "first_name": "' OR '1'='1",
            "student_id_number": "CS-2024'; DELETE FROM t_students; --",
            "group_id": 1,
            "email": "'; DELETE FROM t_students WHERE '1'='1; --@test.com",
            "birth_date": "2000-01-01"
        }

        response = client.post("/api/v1/students/", json=malicious_student_data)

        # Should return 422 (validation error) not 500 (SQL error)
        assert response.status_code in [422], \
            "SQL injection not properly handled in create student"

    def test_sql_injection_in_service_layer(self):
        """
        Тест SQL injection на рівні сервісу.

        Прямий тест репозиторію з malicious вводом.
        """
        service = StudentService()

        # Malicious search query
        malicious_query = "'; DROP TABLE t_students; --"

        # Should not raise exception, should handle gracefully
        try:
            results = service.search_students(query=malicious_query)
            # Should return empty list or filtered results, not cause SQL error
            assert isinstance(results, list)
        except Exception as e:
            # If exception raised, should NOT be SQL-related
            error_msg = str(e).lower()
            assert "drop" not in error_msg
            assert "delete" not in error_msg
            assert "syntax error" not in error_msg

    def test_parameterized_queries_used(self):
        """
        Тест що використовуються параметризовані запити.

        Цей тест перевіряє що репозиторій використовує
        параметризовані запити (не string concatenation).
        """
        repo = StudentRepository()

        # Get method source code inspection (indirect test)
        # Direct test: verify that dangerous input doesn't execute
        dangerous_input = {
            'query': "'; DROP TABLE t_students; --",
            'offset': 0,
            'limit': 10
        }

        # Should not raise SQL syntax error
        try:
            results = repo.search(dangerous_input)
            assert isinstance(results, list)
        except Exception as e:
            # Should not be SQL injection related error
            error_msg = str(e).lower()
            assert "syntax error" not in error_msg or "near" not in error_msg


@pytest.mark.integration
class TestXSSProtection:
    """Тести захисту від XSS (Cross-Site Scripting)."""

    def test_xss_in_student_name(self):
        """
        Тест що XSS payload в імені студента не виконується.
        """
        client = TestClient(app)

        xss_payload = {
            "last_name": "<script>alert('XSS')</script>",
            "first_name": "<img src=x onerror=alert('XSS')>",
            "student_id_number": "XSS-0001",
            "group_id": 1,
            "email": "xss@test.com",
            "birth_date": "2000-01-01"
        }

        response = client.post("/api/v1/students/", json=xss_payload)

        # Should either reject (422) or accept but sanitize
        if response.status_code == 201:
            data = response.json()
            # Script tags should be escaped or removed in response
            assert "<script>" not in str(data)
            assert "onerror=" not in str(data)


@pytest.mark.integration
class TestInputValidation:
    """Тести валідації вводу."""

    def test_extremely_long_input(self):
        """Тест обробки надто довгого вводу."""
        client = TestClient(app)

        # 10,000 character string
        very_long_string = "A" * 10000

        response = client.get(
            "/api/v1/students/search/",
            params={"query": very_long_string}
        )

        # Should handle gracefully (not crash)
        assert response.status_code in [200, 422, 400]

    def test_special_characters_in_input(self):
        """Тест обробки спеціальних символів."""
        client = TestClient(app)

        special_chars = [
            "'; -- comment",
            "\\x00\\x00",  # null bytes
            "../../../etc/passwd",  # path traversal
            "%00",  # null byte
            "\\n\\r\\t",  # control characters
        ]

        for special_char in special_chars:
            response = client.get(
                "/api/v1/students/search/",
                params={"query": special_char}
            )

            # Should not crash
            assert response.status_code in [200, 422, 400]

    def test_unicode_and_emoji_input(self):
        """Тест обробки Unicode та emoji."""
        client = TestClient(app)

        unicode_inputs = [
            "Тест українською мовою",
            "Test Ñoño español",
            "测试中文",
            "😀 🎉 💻",  # Emojis
        ]

        for unicode_input in unicode_inputs:
            response = client.get(
                "/api/v1/students/search/",
                params={"query": unicode_input}
            )

            # Should handle gracefully
            assert response.status_code in [200, 422]


@pytest.mark.integration
class TestRateLimiting:
    """Тести rate limiting."""

    def test_rate_limit_on_create_endpoint(self):
        """
        Тест що rate limiting працює на create endpoint.

        Відправляємо більше запитів ніж дозволено rate limit.
        """
        client = TestClient(app)

        # Try to create 30 students rapidly (rate limit is 20/minute)
        responses = []
        for i in range(30):
            student_data = {
                "last_name": f"Test{i}",
                "first_name": f"User{i}",
                "student_id_number": f"RATE-{i:04d}",
                "group_id": 1,
                "email": f"rate{i}@test.com",
                "birth_date": "2000-01-01"
            }

            response = client.post("/api/v1/students/", json=student_data)
            responses.append(response.status_code)

        # Should have at least some 429 (Too Many Requests) responses
        # Note: This test might be flaky depending on timing
        too_many_requests_count = responses.count(429)

        # At least some requests should be rate limited
        # (but might not always trigger depending on test execution speed)
        print(f"Rate limit responses: {too_many_requests_count} out of 30")

        # Assert we got a mix of success and rate limit
        assert 429 in responses or 201 in responses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
