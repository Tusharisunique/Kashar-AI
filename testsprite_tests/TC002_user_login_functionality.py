import requests

BASE_URL = "http://localhost:3000"
LOGIN_ENDPOINT = "/api/auth/login"
TIMEOUT = 30

VALID_EMAIL = "try.tusharjoshi@gmail.com"
VALID_PASSWORD = "JQLCSG@8"

def test_user_login_functionality():
    # Test login with valid credentials
    valid_payload = {
        "email": VALID_EMAIL,
        "password": VALID_PASSWORD
    }
    try:
        response = requests.post(
            url=BASE_URL + LOGIN_ENDPOINT,
            json=valid_payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Valid login request failed: {e}"
    
    # Validate successful login response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    json_resp = response.json()
    # Assuming the response contains a token or session info token field
    assert "token" in json_resp or "access_token" in json_resp or "session" in json_resp, \
        "Login response missing expected authentication token/session"
    
    # Store token if available for possible session management validation
    token = json_resp.get("token") or json_resp.get("access_token") or json_resp.get("session")
    headers = {}
    if token and isinstance(token, str):
        # Usually Bearer token pattern
        headers = {"Authorization": f"Bearer {token}"}
    
    # Optional: Test session management by verifying access to a protected endpoint if available
    # As no protected endpoint specified for this test, we skip this step.

    # Test login with invalid credentials (wrong password)
    invalid_payload = {
        "email": VALID_EMAIL,
        "password": "wrong_password_123"
    }
    try:
        invalid_resp = requests.post(
            url=BASE_URL + LOGIN_ENDPOINT,
            json=invalid_payload,
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        # Request sent successfully but expect failure response, so no assert here
        invalid_resp = None
        assert False, f"Invalid login request raised exception: {e}"

    assert invalid_resp is not None, "No response received for invalid login attempt"
    # Expected failure status codes often 401 or 403
    assert invalid_resp.status_code in (400, 401, 403), f"Invalid login expected error code, got {invalid_resp.status_code}"
    invalid_json = invalid_resp.json()
    # Check error message presence
    error_msgs = ["error", "message", "detail"]
    assert any(k in invalid_json for k in error_msgs), "Invalid login response missing error message"

test_user_login_functionality()