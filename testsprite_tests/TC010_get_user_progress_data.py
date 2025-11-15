import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:3000"
AUTH_USERNAME = "try.tusharjoshi@gmail.com"
AUTH_PASSWORD = "JQLCSG@8"
TIMEOUT = 30

def test_get_user_progress_data():
    auth = HTTPBasicAuth(AUTH_USERNAME, AUTH_PASSWORD)
    headers = {
        "Accept": "application/json"
    }

    # Test without days parameter
    try:
        response = requests.get(f"{BASE_URL}/api/progress/", auth=auth, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "Response should be a JSON object"
        # Check for keys that likely indicate progress data (analytics, streaks, etc.)
        assert "streak" in data or "analytics" in data or "progress" in data or len(data) > 0, "Response JSON missing expected progress data keys"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    # Test with valid days parameter
    params = {"days": 7}
    try:
        response_days = requests.get(f"{BASE_URL}/api/progress/", auth=auth, headers=headers, params=params, timeout=TIMEOUT)
        assert response_days.status_code == 200, f"Expected status 200 with days=7, got {response_days.status_code}"
        data_days = response_days.json()
        assert isinstance(data_days, dict), "Response with days param should be a JSON object"
        assert "streak" in data_days or "analytics" in data_days or "progress" in data_days or len(data_days) > 0, "Response JSON missing expected progress data keys with days param"
    except requests.RequestException as e:
        assert False, f"Request with days param failed: {e}"

    # Test with invalid days parameter (e.g., negative)
    params_invalid = {"days": -5}
    try:
        response_invalid = requests.get(f"{BASE_URL}/api/progress/", auth=auth, headers=headers, params=params_invalid, timeout=TIMEOUT)
        # Depending on implementation, API may return 400 or 200 with error info
        assert response_invalid.status_code in (200, 400), f"Expected status 200 or 400 for invalid days, got {response_invalid.status_code}"
        if response_invalid.status_code == 200:
            json_resp = response_invalid.json()
            # Possibly an empty progress or an error message inside
            assert isinstance(json_resp, dict), "Response for invalid days param should be JSON object"
        else:
            # 400 Bad Request - error response must contain error message
            json_resp = response_invalid.json()
            assert "error" in json_resp or "message" in json_resp, "Error response missing error/message key"
    except requests.RequestException as e:
        assert False, f"Request with invalid days param failed: {e}"

test_get_user_progress_data()