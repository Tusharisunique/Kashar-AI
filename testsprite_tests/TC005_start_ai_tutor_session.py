import requests

BASE_URL = "http://localhost:3000"
TIMEOUT = 30

def test_start_ai_tutor_session():
    session_types = ["text", "voice"]
    headers = {
        "Content-Type": "application/json"
    }
    for session_type in session_types:
        payload = {"session_type": session_type}
        try:
            response = requests.post(
                f"{BASE_URL}/api/tutor/start-session",
                json=payload,
                headers=headers,
                timeout=TIMEOUT
            )
            # Assert success status code
            assert response.status_code == 200, f"Unexpected status code {response.status_code} for session_type {session_type}"
            data = response.json()
            # Validate response contains session context initialized keys, typically session_id or context
            assert "session_id" in data and isinstance(data["session_id"], str) and data["session_id"], "Missing or invalid 'session_id'"
            # Optionally check any context details if provided
            if "context" in data:
                assert isinstance(data["context"], dict), "'context' should be a dictionary"
        except requests.RequestException as e:
            assert False, f"Request failed for session_type {session_type}: {str(e)}"

test_start_ai_tutor_session()