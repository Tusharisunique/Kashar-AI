import requests
from requests.auth import HTTPBasicAuth

def test_get_user_documents_api():
    base_url = "http://localhost:8000"
    endpoint = "/api/documents/"
    url = base_url + endpoint
    auth = HTTPBasicAuth("try.tusharjoshi@gmail.com", "JQLCSG@8")
    headers = {
        "Accept": "application/json"
    }
    timeout = 30

    try:
        # Make GET request to fetch user documents
        response = requests.get(url, auth=auth, headers=headers, timeout=timeout)

        # Assert response status code is 200 OK
        assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

        # Assert response content-type is application/json
        assert "application/json" in response.headers.get("Content-Type", ""), "Response is not JSON"

        documents = response.json()

        # Assert the response is a list (documents)
        assert isinstance(documents, list), "Documents response is not a list"

        # Validate each document item structure for security and correctness
        for doc in documents:
            # Check keys presence
            required_keys = {"id", "filename", "uploaded_at", "size", "mime_type"}
            assert required_keys.issubset(doc.keys()), f"Document missing keys: {required_keys - doc.keys()}"

            # Validate types to avoid injection or malformed data
            assert isinstance(doc["id"], (str, int)), "Document id should be string or int"
            assert isinstance(doc["filename"], str) and doc["filename"].strip() != "", "Invalid filename"
            assert isinstance(doc["uploaded_at"], str), "Invalid uploaded_at format"
            assert isinstance(doc["size"], int) and doc["size"] >= 0, "Invalid document size"
            assert isinstance(doc["mime_type"], str) and "/" in doc["mime_type"], "Invalid mime_type value"

            # Basic XSS check: filename should not contain script tags or suspicious chars
            suspicious_strings = ["<script>", "</script>", "javascript:", "onerror", "onload"]
            filename_lower = doc["filename"].lower()
            for s in suspicious_strings:
                assert s not in filename_lower, f"Potential XSS risk in filename: {doc['filename']}"

    except requests.exceptions.Timeout:
        assert False, "Request timed out"
    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {str(e)}"

test_get_user_documents_api()