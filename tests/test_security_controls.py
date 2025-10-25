from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestEnhancedInputValidation:
    def test_create_user_weak_password(self):
        response = client.post(
            "/users",
            json={"name": "testuser", "email": "test@example.com", "password": "weak"},
        )
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    def test_create_user_no_uppercase_password(self):
        response = client.post(
            "/users",
            json={
                "name": "testuser",
                "email": "test@example.com",
                "password": "lowercase123",
            },
        )
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    def test_create_user_invalid_username(self):
        response = client.post(
            "/users",
            json={
                "name": "invalid@name",
                "email": "test@example.com",
                "password": "ValidPass123",
            },
        )
        assert response.status_code == 422

    def test_create_user_sql_injection_attempt(self):
        response = client.post(
            "/users",
            json={
                "name": "admin'; DROP TABLE users--",
                "email": "test@example.com",
                "password": "ValidPass123",
            },
        )
        assert response.status_code == 422


class TestSecureErrorHandling:
    def test_error_response_sanitization(self, test_db_engine):
        response = client.get("/users/9999")
        error_data = response.json()

        assert "type" in error_data
        assert "correlation_id" in error_data
        assert "stack" not in str(error_data).lower()

    def test_password_not_in_logs(self, test_db_engine, caplog):
        with caplog.at_level("ERROR"):
            client.post(
                "/users",
                json={
                    "name": "test",
                    "email": "test@example.com",
                    "password": "SuperSecret123",
                },
            )

        log_text = "\n".join(record.message for record in caplog.records)
        assert "SuperSecret123" not in log_text


class TestSecurityHeaders:
    def test_security_headers_present(self):
        response = client.get("/health")

        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
        }

        for header, expected_value in required_headers.items():
            assert header in response.headers
            assert response.headers[header] == expected_value

    def test_sensitive_headers_removed(self):
        response = client.get("/health")
        assert "server" not in response.headers
        assert "x-powered-by" not in response.headers
