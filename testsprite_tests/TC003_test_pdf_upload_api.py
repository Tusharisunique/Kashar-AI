import requests

BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = "/api/documents/upload"
TIMEOUT = 30

def test_pdf_upload_api():
    headers = {
        "Accept": "application/json"
    }
    # Using a minimal valid PDF file binary to test upload
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] >>\nendobj\n"
        b"trailer\n<< /Root 1 0 R >>\n%%EOF"
    )
    files = {
        "file": ("test_document.pdf", pdf_content, "application/pdf")
    }

    try:
        response = requests.post(
            BASE_URL + UPLOAD_ENDPOINT,
            headers=headers,
            files=files,
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        assert False, f"Request to upload PDF failed: {e}"

    # Validate status code for success (201 Created or 200 OK)
    assert response.status_code in (200, 201), f"Unexpected status code: {response.status_code} - {response.text}"

    # Validate response content for expected data indicating parsing success and storage
    try:
        json_response = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # Check for presence of expected keys in response indicating successful parsing and storage
    # e.g., file_id, status, parsed_data or similar
    expected_keys = ["file_id", "status"]
    for key in expected_keys:
        assert key in json_response, f"Response JSON missing key: {key}"

    # Status should indicate success
    assert json_response["status"].lower() in ["success", "uploaded", "processed"], f"Unexpected status value: {json_response.get('status')}"

    # Additional checks for security:
    # Ensure no sensitive information returned
    disallowed_keys = ["password", "token", "credentials", "auth"]
    for key in disallowed_keys:
        assert key not in json_response, f"Sensitive info '{key}' should not be in response"

    # Validate file_id is non-empty and valid format (string, not a SQL injection string)
    file_id = json_response.get("file_id")
    assert isinstance(file_id, str) and len(file_id) > 0, "Invalid or missing file_id"

    # Basic check against SQL injection or XSS patterns in file_id or other fields
    suspicious_patterns = ["'", '"', ";", "--", "<", ">", "`"]
    for pattern in suspicious_patterns:
        assert pattern not in file_id, f"Potential injection pattern '{pattern}' found in file_id"

    # The API should NOT echo uploaded file content or raw data (to prevent XSS)
    raw_resp_str = response.text.lower()
    assert "<script>" not in raw_resp_str and "<img" not in raw_resp_str, "Response contains potential XSS vectors"

    # Confirm content-type header is JSON
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type.lower(), f"Unexpected Content-Type: {content_type}"

test_pdf_upload_api()
