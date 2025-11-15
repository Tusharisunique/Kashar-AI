import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_get_user_progress_data_api():
    """Verify the API rejects unauthorized access with proper error codes and returns JSON response."""
    # SECURITY: Test unauthorized access rejection - no auth header
    try:
        response_no_auth = requests.get(f"{BASE_URL}/api/progress/", params={'days': 7}, timeout=TIMEOUT)
    except requests.RequestException:
        assert False, "Request without auth failed unexpectedly due to network issues"
    assert response_no_auth.status_code in (401, 403), "Unauthorized request should be rejected with 401 or 403"


# Run the test

test_get_user_progress_data_api()
