import requests
import re

BASE_URL = "http://localhost:8000"
SIGNUP_ENDPOINT = "/api/auth/signup"
TIMEOUT = 30

def test_user_signup_api():
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Valid signup payload
    valid_email = "testuser_security_check@example.com"
    valid_password = "Str0ngP@ssw0rd!"
    valid_payload = {
        "email": valid_email,
        "password": valid_password
    }

    # Test successful signup with valid data
    try:
        response = requests.post(
            BASE_URL + SIGNUP_ENDPOINT,
            json=valid_payload,
            headers=headers,
            timeout=TIMEOUT
        )
        assert response.status_code == 201 or response.status_code == 200, f"Expected 201 or 200 but got {response.status_code}"
        data = response.json()
        # Should not expose sensitive data like password in response
        assert "password" not in data, "Response should not contain password field"
        # Basic email confirmation pattern
        assert re.match(r"[^@]+@[^@]+\.[^@]+", data.get("email", "")), "Email format invalid in response"
        # Check no SQL injection or script tags in response fields
        for key, value in data.items():
            if isinstance(value, str):
                assert "<script>" not in value.lower(), f"Response contains potential XSS in field {key}"
                assert ";" not in value and "--" not in value, f"Response contains potential SQL injection artifacts in field {key}"

    except requests.RequestException as e:
        assert False, f"Request failed during valid signup test: {e}"

    # Test invalid email formats
    invalid_emails = [
        "plainaddress",
        "@no-local-part.com",
        "Outlook Contact <outlook-contact@domain.com>",
        "no-at.domain.com",
        "no-tld@domain",
        ";DROP TABLE users;@example.com",
        "<script>alert(1)</script>@example.com"
    ]
    for email in invalid_emails:
        payload = {
            "email": email,
            "password": valid_password
        }
        try:
            resp = requests.post(
                BASE_URL + SIGNUP_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=TIMEOUT
            )
            # Expecting client error 400 or similar for validation failure
            assert resp.status_code in (400, 422), f"Invalid email '{email}' did not reject properly, status {resp.status_code}"
            error_resp = resp.json()
            # Should have some error message related to email validation
            error_msgs = str(error_resp).lower()
            assert ("email" in error_msgs) or ("invalid" in error_msgs) or ("format" in error_msgs), "Error response should indicate email format issue"
        except requests.RequestException as e:
            assert False, f"Request failed during invalid email test '{email}': {e}"

    # Test invalid passwords (too short, no complexity, injection attempts, script tags)
    invalid_passwords = [
        "short",                        # too short
        "alllowercase",                 # no uppercase, no digit, no symbol
        "ALLUPPERCASE",                 # no lowercase, no digit, no symbol
        "12345678",                    # no letters or symbols
        "password<script>alert('x')</script>",  # xss injection
        "password; DROP TABLE users;",           # sql injection
        "' OR '1'='1",                     # classic sql injection string
    ]
    for pwd in invalid_passwords:
        payload = {
            "email": "validemailforsafety@example.com",
            "password": pwd
        }
        try:
            resp = requests.post(
                BASE_URL + SIGNUP_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=TIMEOUT
            )
            # Expecting client error 400 or 422 for invalid password
            assert resp.status_code in (400, 422), f"Invalid password '{pwd}' did not reject properly, status {resp.status_code}"
            err_resp = resp.json()
            error_text = str(err_resp).lower()
            assert ("password" in error_text) or ("invalid" in error_text) or ("complexity" in error_text) or ("weak" in error_text), \
                "Error response should indicate password validation failure"
        except requests.RequestException as e:
            assert False, f"Request failed during invalid password test '{pwd}': {e}"

    # Test SQL Injection attempt in email and password combined
    injection_payload = {
        "email": "' OR '1'='1@example.com",
        "password": "' OR '1'='1"
    }
    try:
        resp = requests.post(
            BASE_URL + SIGNUP_ENDPOINT,
            json=injection_payload,
            headers=headers,
            timeout=TIMEOUT
        )
        assert resp.status_code in (400, 422), f"SQL Injection payload did not get rejected, status {resp.status_code}"
        error_data = resp.json()
        error_msg = str(error_data).lower()
        # Ensure no internal error or stack trace revealed
        assert "error" in error_msg or "invalid" in error_msg or "reject" in error_msg or "sql" in error_msg or "injection" in error_msg or "bad" in error_msg, \
            "Error message should indicate rejection of injection inputs"
    except requests.RequestException as e:
        assert False, f"Request failed during SQL injection test: {e}"


test_user_signup_api()