import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:3000"
USERNAME = "try.tusharjoshi@gmail.com"
PASSWORD = "JQLCSG@8"
TIMEOUT = 30


def test_get_user_documents():
    url = f"{BASE_URL}/api/documents/"
    try:
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to get user documents failed: {e}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # Expecting a list or dict with documents info; verify structure
    assert isinstance(data, (list, dict)), "Response JSON should be a list or dict"

    # If list, verify each document has at least id and user-related info
    if isinstance(data, list):
        for doc in data:
            assert isinstance(doc, dict), "Each document should be a JSON object"
            assert "id" in doc, "Document should contain 'id'"
            # Optionally check for other common keys like filename or uploaded date
            # place here any other document validations if needed
    elif isinstance(data, dict):
        # If dict, check keys typical for documents collection
        assert "documents" in data or "items" in data or len(data) > 0, "Expected keys for documents in response"

    # Additional sanity check: documents should belong to the authenticated user
    # This depends on response schema. If userId or email present, verify it matches USERNAME.
    for doc in (data if isinstance(data, list) else data.get("documents", [])):
        if isinstance(doc, dict):
            user_email = doc.get("user_email") or doc.get("owner_email")
            if user_email:
                assert user_email == USERNAME, "Document does not belong to the authenticated user"

    print("test_get_user_documents passed")


test_get_user_documents()