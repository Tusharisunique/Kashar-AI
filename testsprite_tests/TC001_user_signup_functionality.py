import requests

BASE_URL = "http://localhost:3000"
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 30

def test_user_signup_functionality():
    signup_url = f"{BASE_URL}/api/auth/signup"

    # Valid signup data
    valid_user = {
        "email": "testuser_valid@example.com",
        "password": "ValidPass123!"
    }

    # Invalid signup data cases
    invalid_users = [
        # Missing email
        {"password": "ValidPass123!"},
        # Missing password
        {"email": "testuser_invalid@example.com"},
        # Invalid email format
        {"email": "invalid-email-format", "password": "ValidPass123!"},
        # Password too short
        {"email": "testuser_shortpass@example.com", "password": "123"},
        # Empty email
        {"email": "", "password": "ValidPass123!"},
        # Empty password
        {"email": "testuser_empty@example.com", "password": ""}
    ]

    # Attempt valid signup
    try:
        response = requests.post(signup_url, json=valid_user, headers=HEADERS, timeout=TIMEOUT)
        assert response.status_code == 201 or response.status_code == 200, f"Expected 201 or 200 but got {response.status_code}"
        data = response.json()
        assert "email" in data and data["email"] == valid_user["email"], "Response email does not match signup email"
    finally:
        # Cleanup: Attempt to delete the created user via login and then delete if such API existed
        # Since no delete user endpoint provided, this is a placeholder for cleanup if needed.
        pass

    # Test invalid signups and verify error responses
    for user_payload in invalid_users:
        response = requests.post(signup_url, json=user_payload, headers=HEADERS, timeout=TIMEOUT)
        # Expect client error status code for invalid input, commonly 400 or 422
        assert response.status_code in {400, 422}, f"For payload {user_payload}, expected 400 or 422 but got {response.status_code}"
        error_data = None
        try:
            error_data = response.json()
        except Exception:
            pass
        assert error_data is not None, "Expected error message in response but got none"
        # Check for common error keys or messages that indicate invalid input
        error_message_found = any(
            key in error_data for key in ["error", "message", "errors"]
        )
        assert error_message_found, f"Response for invalid input missing error message: {error_data}"

test_user_signup_functionality()