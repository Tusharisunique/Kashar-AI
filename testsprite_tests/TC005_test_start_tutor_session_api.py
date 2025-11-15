import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"
AUTH_USERNAME = "try.tusharjoshi@gmail.com"
AUTH_PASSWORD = "JQLCSG@8"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json"}

def test_start_tutor_session_api():
    auth = HTTPBasicAuth(AUTH_USERNAME, AUTH_PASSWORD)
    url = f"{BASE_URL}/api/tutor/start-session"

    # Valid session types to test
    valid_session_types = ["text", "voice"]
    for session_type in valid_session_types:
        try:
            response = requests.post(
                url,
                json={"session_type": session_type},
                headers=HEADERS,
                auth=auth,
                timeout=TIMEOUT
            )
            assert response.status_code == 201 or response.status_code == 200, \
                f"Expected success status code for session_type={session_type}, got {response.status_code}"
            json_response = response.json()
            assert "session_id" in json_response and isinstance(json_response["session_id"], str) and json_response["session_id"], \
                f"Response missing valid session_id for session_type={session_type}"
        except requests.exceptions.RequestException as e:
            assert False, f"RequestException for session_type={session_type}: {e}"

    # Invalid session types to test input validation
    invalid_session_types = [
        "",  # Empty string
        "TEXT",  # Case-sensitive test
        "vo1ce",  # Injection vector attempt
        "<script>alert(1)</script>",  # XSS attempt
        "text; DROP TABLE users;",  # SQL injection attempt
        None,
        123,
        {},
        [],
        "text\nvoice",
    ]

    for invalid_type in invalid_session_types:
        payload = {"session_type": invalid_type}
        try:
            response = requests.post(
                url,
                json=payload,
                headers=HEADERS,
                auth=auth,
                timeout=TIMEOUT
            )
            # Expecting 400 Bad Request or similar error code for invalid input
            assert response.status_code == 400 or response.status_code == 422 or response.status_code == 401, \
                f"Expected error status code for invalid session_type={invalid_type}, got {response.status_code}"

            # Response should contain error details without leaking sensitive info
            json_response = response.json()
            assert "error" in json_response or "detail" in json_response, \
                f"Expected error message in response for invalid session_type={invalid_type}"
            # Check error message does not expose system internals (basic check)
            error_msg = json_response.get("error") or json_response.get("detail") or ""
            assert "traceback" not in error_msg.lower() and "exception" not in error_msg.lower(), \
                f"Error message should not leak internal details: {error_msg}"
        except requests.exceptions.RequestException as e:
            assert False, f"RequestException for invalid session_type={invalid_type}: {e}"

    # Test authentication failure scenarios
    try:
        response = requests.post(
            url,
            json={"session_type": "text"},
            headers=HEADERS,
            auth=HTTPBasicAuth("invalid_user@example.com", "wrong_password"),
            timeout=TIMEOUT
        )
        assert response.status_code == 401 or response.status_code == 403, \
            f"Expected authentication failure with invalid credentials, got {response.status_code}"
    except requests.exceptions.RequestException as e:
        assert False, f"RequestException during authentication failure test: {e}"

test_start_tutor_session_api()