import requests

BASE_URL = "http://localhost:8000"
EMAIL = "try.tusharjoshi@gmail.com"
PASSWORD = "JQLCSG@8"
TIMEOUT = 30


def test_send_message_to_ai_tutor_api():
    headers = {"Content-Type": "application/json"}

    # Perform login to get token
    login_payload = {"email": EMAIL, "password": PASSWORD}
    login_resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=login_payload,
        headers=headers,
        timeout=TIMEOUT
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    login_data = login_resp.json()
    # Assuming token is returned under 'access_token' or similar
    token = login_data.get('access_token') or login_data.get('token') or login_data.get('session_token')
    assert token and isinstance(token, str), "No valid token in login response"

    auth_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    session_id = None

    try:
        # Start a new tutor session with valid session_type "text"
        start_session_payload = {"session_type": "text"}
        start_resp = requests.post(
            f"{BASE_URL}/api/tutor/start-session",
            json=start_session_payload,
            headers=auth_headers,
            timeout=TIMEOUT
        )
        assert start_resp.status_code == 200, f"Failed to start session: {start_resp.text}"
        start_data = start_resp.json()
        assert "session_id" in start_data, "Response missing session_id"
        session_id = start_data["session_id"]
        assert isinstance(session_id, str) and len(session_id) > 0, "Invalid session_id"

        # Prepare a safe, valid message payload to avoid injection or XSS risks
        message_payload = {
            "message": "Explain the Pythagorean theorem.",
            "session_id": session_id
        }

        # Send message to AI tutor
        message_resp = requests.post(
            f"{BASE_URL}/api/tutor/message",
            json=message_payload,
            headers=auth_headers,
            timeout=TIMEOUT
        )
        assert message_resp.status_code == 200, f"Failed to send message: {message_resp.text}"
        message_data = message_resp.json()

        # Validate response structure and content
        assert isinstance(message_data, dict), "Expected JSON object in response"
        # Check for presence of some fields typically expected in AI response
        assert "response" in message_data, "AI response missing 'response' field"
        ai_response = message_data["response"]
        assert isinstance(ai_response, str) and len(ai_response) > 0, "AI response is empty or invalid"

        # Security: Ensure no unexpected HTML/script tags in response to prevent XSS
        forbidden_substrings = ["<script>", "</script>", "javascript:", "onerror=", "onload="]
        for substr in forbidden_substrings:
            assert substr not in ai_response.lower(), f"Potential XSS vulnerability detected in response: {substr}"

        # Security: Check the message send endpoint rejects or properly escapes injection attempts
        injection_payload = {
            "message": "'; DROP TABLE users; --",
            "session_id": session_id
        }
        inj_resp = requests.post(
            f"{BASE_URL}/api/tutor/message",
            json=injection_payload,
            headers=auth_headers,
            timeout=TIMEOUT
        )
        # Accept either a handled error or a safe response
        assert inj_resp.status_code in (200, 400, 422), f"Unexpected status for injection attempt: {inj_resp.status_code}"
        if inj_resp.status_code == 200:
            inj_data = inj_resp.json()
            inj_response_text = inj_data.get("response", "").lower()
            # Should not execute injection - response should not contain SQL error or sensitive info
            assert "error" not in inj_response_text and "sql" not in inj_response_text, "Potential SQL injection vulnerability"
        else:
            # For error responses, check proper error message
            error_json = inj_resp.json()
            assert "error" in error_json or "detail" in error_json, "No error info on invalid input"

    finally:
        # Attempt to clean up / invalidate session by calling an assumed session delete API if exists
        if session_id:
            try:
                delete_resp = requests.delete(
                    f"{BASE_URL}/api/tutor/end-session",
                    json={"session_id": session_id},
                    headers=auth_headers,
                    timeout=TIMEOUT
                )
                # Accept 200 or 404 (already ended or removed)
                assert delete_resp.status_code in (200, 404)
            except Exception:
                pass


test_send_message_to_ai_tutor_api()