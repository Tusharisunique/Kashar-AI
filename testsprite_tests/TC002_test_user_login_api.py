import requests

BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = "/api/auth/login"
TIMEOUT = 30

def test_user_login_api():
    url = BASE_URL + LOGIN_ENDPOINT
    headers = {
        "Content-Type": "application/json"
    }

    # Valid credentials from instructions
    valid_payload = {
        "email": "try.tusharjoshi@gmail.com",
        "password": "JQLCSG@8"
    }

    # Invalid credentials to test failure and security
    invalid_payloads = [
        # Wrong password
        {"email": "try.tusharjoshi@gmail.com", "password": "wrongpassword"},
        # SQL Injection attempt in email
        {"email": "try.tusharjoshi@gmail.com' OR '1'='1", "password": "any"},
        # SQL Injection attempt in password
        {"email": "try.tusharjoshi@gmail.com", "password": "' OR '1'='1"},
        # XSS attempt in email field
        {"email": "<script>alert('xss')</script>@gmail.com", "password": "JQLCSG@8"},
        # Empty email and password
        {"email": "", "password": ""},
        # Missing fields
        {"email": "try.tusharjoshi@gmail.com"},
        {"password": "JQLCSG@8"},
    ]

    # Test successful login with valid credentials
    try:
        resp = requests.post(url, json=valid_payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed with exception for valid credentials: {e}"

    # Assert HTTP 200 OK for successful login
    assert resp.status_code == 200, f"Expected status 200 for valid login but got {resp.status_code}"

    # Assert that response includes a session token (assuming field 'token' or similar)
    try:
        resp_json = resp.json()
    except ValueError:
        assert False, "Response to valid login is not valid JSON"

    # Check for presence and type of the token value
    token = resp_json.get("token") or resp_json.get("access_token") or resp_json.get("session_token")
    assert token and isinstance(token, str) and len(token) > 0, "No valid session token received on successful login"

    # Check that token does not contain suspicious characters that could indicate injection or XSS
    suspicious_chars = ['<', '>', '"', "'", ';', '--']
    assert not any(c in token for c in suspicious_chars), "Session token contains suspicious characters"

    # Test failure cases with invalid credentials and check for proper error messages/status codes
    for idx, payload in enumerate(invalid_payloads):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"Request failed with exception for invalid payload #{idx+1}: {e}"

        # Expecting 400, 401 or 422 for invalid login attempts
        assert resp.status_code in (400, 401, 422), f"Expected 400, 401 or 422 for invalid login but got {resp.status_code} for payload #{idx+1}"

        try:
            resp_json = resp.json()
        except ValueError:
            # Error responses should be JSON formatted
            assert False, f"Error response #{idx+1} is not valid JSON"

        # Check that error message does not disclose sensitive internal info
        message = None
        for key in ["message", "error", "detail"]:
            val = resp_json.get(key)
            if isinstance(val, str) and len(val) > 0:
                message = val
                break

        assert message is not None, f"Error message field missing or not string in response #{idx+1}"

        # Ensure error messages are generic and avoid revealing DB or injection details
        forbidden_info = [
            "syntax error", "sql", "exception", "traceback", "ora-", "psql", "mysql", "server error"
        ]
        lowered_msg = message.lower()
        assert not any(term in lowered_msg for term in forbidden_info), f"Error message disclosure in response #{idx+1}"

    # Check that rate limiting or account lockout / throttling headers or info might be present (optional- based on API)
    # This is to mitigate brute force attacks but can be checked if API supports.
    # Not implemented here due to API info absence.

test_user_login_api()
