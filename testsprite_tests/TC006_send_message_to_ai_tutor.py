import requests

BASE_URL = "http://localhost:3000"
AUTH_CREDENTIALS = ("try.tusharjoshi@gmail.com", "JQLCSG@8")
TIMEOUT = 30

def test_send_message_to_ai_tutor():
    headers = {
        "Content-Type": "application/json"
    }
    try:
        # Step 1: Authenticate user to obtain an auth token if any
        # Since "basic token" auth is specified as username/password, try logging in first to get any token or session if supported.
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": AUTH_CREDENTIALS[0], "password": AUTH_CREDENTIALS[1]},
            timeout=TIMEOUT
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        login_data = login_resp.json()
        # Assume token is returned under 'access_token' or similar key; fallback to no token if absent
        token = login_data.get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # Step 2: Start a new AI tutor session to get session_id
        start_session_payload = {"session_type": "text"}
        start_session_resp = requests.post(
            f"{BASE_URL}/api/tutor/start-session",
            json=start_session_payload,
            headers=headers,
            timeout=TIMEOUT
        )
        assert start_session_resp.status_code == 200, f"Start session failed: {start_session_resp.text}"
        session_data = start_session_resp.json()
        session_id = session_data.get("session_id")
        assert session_id, "No session_id returned from start-session"

        # Step 3: Send a message to the AI tutor with this session_id
        message_content = "Explain the concept of photosynthesis."
        message_payload = {"session_id": session_id, "message": message_content}
        message_resp = requests.post(
            f"{BASE_URL}/api/tutor/message",
            json=message_payload,
            headers=headers,
            timeout=TIMEOUT
        )
        assert message_resp.status_code == 200, f"Message sending failed: {message_resp.text}"
        message_resp_data = message_resp.json()
        # Validate that response includes a reply relevant to the message content
        # Expect response to contain "reply" or "response" field with a string answer
        # This field is assumed from context, adjust if PRD indicates differently
        valid_keys = ["reply", "response", "answer", "message"]  # possible keys
        response_text = None
        for key in valid_keys:
            if key in message_resp_data and isinstance(message_resp_data[key], str):
                response_text = message_resp_data[key]
                break
        assert response_text and len(response_text) > 0, "AI tutor response is empty or missing"

        # Optionally check contextual relevance: basic keyword presence
        assert "photosynthesis" in response_text.lower(), "Response does not seem contextually relevant"

    finally:
        # Cleanup: End the tutor session if API supports session deletion or ending
        # No explicit endpoint for DELETE session mentioned in PRD, so just skip cleanup
        pass

test_send_message_to_ai_tutor()