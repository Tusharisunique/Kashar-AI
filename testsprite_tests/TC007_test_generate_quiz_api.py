import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"
AUTH_CREDENTIALS = HTTPBasicAuth("try.tusharjoshi@gmail.com", "JQLCSG@8")
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
TIMEOUT = 30

def test_generate_quiz_api():
    url = f"{BASE_URL}/api/quiz/generate"
    # Test Inputs - valid data
    payload_valid = {
        "topic": "Mathematics",
        "difficulty": "medium",
        "num_questions": 5
    }
    # Test Inputs - input validation / injection attempt
    payload_injection = {
        "topic": "'; DROP TABLE users; --",
        "difficulty": "easy",
        "num_questions": 3
    }
    payload_xss = {
        "topic": "<script>alert('XSS')</script>",
        "difficulty": "easy",
        "num_questions": 3
    }
    # List of payloads to test normal and malicious inputs
    test_payloads = [payload_valid, payload_injection, payload_xss]

    for payload in test_payloads:
        try:
            response = requests.post(url, json=payload, headers=HEADERS, auth=AUTH_CREDENTIALS, timeout=TIMEOUT)
            # Common security-related checks
            
            # Assert the response status code
            # Accept either 200 for valid or 400 for invalid inputs
            assert response.status_code in (200, 400), f"Unexpected status code: {response.status_code} for payload: {payload}"

            content_type = response.headers.get("Content-Type", "")
            assert content_type.startswith("application/json"), f"Response content type is not JSON: {content_type}"

            json_resp = response.json()
            
            if response.status_code == 200:
                # Validate response schema for generated quiz
                # Should include 'quiz_id' (string), and 'questions' (list)
                assert "quiz_id" in json_resp and isinstance(json_resp["quiz_id"], str) and json_resp["quiz_id"], "Missing or invalid quiz_id"
                assert "questions" in json_resp and isinstance(json_resp["questions"], list), "Missing or invalid questions list"
                # Ensure number of questions matches requested number (if present)
                assert len(json_resp["questions"]) == payload["num_questions"], "Mismatch in number of questions generated"
                # Validate question contents are safe strings (no scripts)
                for question in json_resp["questions"]:
                    assert isinstance(question, dict), "Each question must be a dict"
                    question_text = question.get("question_text") or question.get("text") or ""
                    assert isinstance(question_text, str), "Question text must be string"
                    # Basic XSS prevention check: question text should not contain script tags
                    assert "<script" not in question_text.lower(), "Potential XSS in question text"
                    # Further check question text content to avoid injection evidence
                    forbidden_sequences = [";", "--", "DROP TABLE", "DELETE FROM", "' OR '1'='1"]
                    for seq in forbidden_sequences:
                        assert seq.lower() not in question_text.lower(), f"Potential SQL Injection pattern found in question text: {seq}"
            else:
                # For invalid inputs, validate error message present and no sensitive info leaked
                assert "error" in json_resp or "message" in json_resp, "Error message expected for invalid input"
                error_msg = json_resp.get("error") or json_resp.get("message")
                assert isinstance(error_msg, str), "Error message must be a string"
                # Ensure no internal stack traces or DB errors are leaked
                forbidden_error_terms = ["traceback", "sqlalchemy", "exception", "syntax error", "unhandled"]
                for term in forbidden_error_terms:
                    assert term not in error_msg.lower(), f"Internal error detail leaked: {term}"
        except requests.exceptions.RequestException as e:
            assert False, f"Request failed unexpectedly: {e}"
        except ValueError as e:
            assert False, f"Response not JSON or invalid JSON: {e}"


test_generate_quiz_api()