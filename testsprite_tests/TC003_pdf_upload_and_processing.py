import requests
from requests.auth import HTTPBasicAuth
from io import BytesIO

BASE_URL = "http://localhost:3000"
UPLOAD_ENDPOINT = "/api/documents/upload"
DOCUMENTS_ENDPOINT = "/api/documents/"

USERNAME = "try.tusharjoshi@gmail.com"
PASSWORD = "JQLCSG@8"

TIMEOUT = 30

def test_pdf_upload_and_processing():
    # Prepare authentication
    auth = HTTPBasicAuth(USERNAME, PASSWORD)
    headers = {}
    
    # Minimal valid PDF bytes to simulate a PDF file in memory
    pdf_content = b"%PDF-1.4\n%EOF\n"
    files = {
        "file": ("test_sample.pdf", BytesIO(pdf_content), "application/pdf")
    }

    # Upload the PDF document
    response = requests.post(
        BASE_URL + UPLOAD_ENDPOINT,
        auth=auth,
        headers=headers,
        files=files,
        timeout=TIMEOUT
    )

    # Validate the upload response is successful
    assert response.status_code == 200 or response.status_code == 201, f"Unexpected status code: {response.status_code}, body: {response.text}"

    # Validate response content for success (assuming JSON with some confirmation or document id)
    try:
        data = response.json()
    except Exception as e:
        assert False, f"Response is not valid JSON: {e}"

    # Basic checks on returned data
    assert isinstance(data, dict), f"Response JSON is not an object: {data}"
    assert "id" in data or "document_id" in data or "message" in data, f"Expected keys missing in response: {data}"

    # Optionally verify the document is listed in user's documents to confirm storage in ChromaDB
    docs_response = requests.get(
        BASE_URL + DOCUMENTS_ENDPOINT,
        auth=auth,
        timeout=TIMEOUT
    )
    assert docs_response.status_code == 200, f"Failed to fetch documents, status: {docs_response.status_code}, body: {docs_response.text}"
    try:
        docs_data = docs_response.json()
    except Exception as e:
        assert False, f"Documents response is not valid JSON: {e}"

    # Should be a list of documents
    assert isinstance(docs_data, list), f"Documents response is not a list: {docs_data}"

    # Check that uploaded document is found by matching document id or minimal check by message
    if "id" in data:
        uploaded_doc_id = data["id"]
        found = any(doc.get("id") == uploaded_doc_id for doc in docs_data)
        assert found, "Uploaded document id not found in user documents"
    else:
        # fallback, just ensure docs list is not empty after upload
        assert len(docs_data) > 0, "Documents list is empty after upload"

test_pdf_upload_and_processing()