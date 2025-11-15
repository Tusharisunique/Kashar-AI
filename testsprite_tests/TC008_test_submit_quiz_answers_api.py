import requests

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
QUIZ_GENERATE_URL = f"{BASE_URL}/api/quiz/generate"
QUIZ_SUBMIT_URL = f"{BASE_URL}/api/quiz/submit"
TIMEOUT = 30

AUTH_EMAIL = "try.tusharjoshi@gmail.com"
AUTH_PASSWORD = "JQLCSG@8"

def test_submit_quiz_answers_api():
    # Step 1: Login to get the auth token
    login_payload = {
        "email": AUTH_EMAIL,
        "password": AUTH_PASSWORD
    }
    login_response = requests.post(LOGIN_URL, json=login_payload, timeout=TIMEOUT)
    assert login_response.status_code == 200, f"Login failed with status {login_response.status_code}"
    login_json = login_response.json()
    assert "access_token" in login_json, "Login response missing access_token"

    token = login_json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    quiz_payload = {
        "topic": "sample topic for testing",
        "difficulty": "easy",
        "num_questions": 3
    }

    # Generate a quiz first to obtain quiz_id and valid answers length
    gen_response = requests.post(QUIZ_GENERATE_URL, json=quiz_payload, headers=headers, timeout=TIMEOUT)
    assert gen_response.status_code in (200, 201), f"Expected status 200/201 but got {gen_response.status_code}"
    gen_json = gen_response.json()

    # Validate the response structure and presence of quiz_id and questions
    assert "quiz_id" in gen_json, "Response missing quiz_id"
    assert "questions" in gen_json and isinstance(gen_json["questions"], list), "Response missing questions list"
    assert len(gen_json["questions"]) == quiz_payload["num_questions"], "Mismatch in number of questions generated"

    quiz_id = gen_json["quiz_id"]

    # Prepare answers assuming all answers are integers as per schema
    answers = [0] * quiz_payload["num_questions"]

    submit_payload = {
        "quiz_id": quiz_id,
        "answers": answers
    }

    # Submit the quiz answers
    submit_response = requests.post(QUIZ_SUBMIT_URL, json=submit_payload, headers=headers, timeout=TIMEOUT)
    assert submit_response.status_code == 200, f"Submission failed with status {submit_response.status_code}"
    submit_json = submit_response.json()

    # Validate submission response - expect success flag and user progress update
    assert isinstance(submit_json, dict), "Submission response is not a JSON object"
    assert "success" in submit_json and submit_json["success"] is True, "Submission not successful"
    assert "results" in submit_json and isinstance(submit_json["results"], dict), "Missing or invalid results data"
    assert "user_progress" in submit_json, "User progress data missing"

    # Security checks - response fields should not contain harmful scripts or injections
    def check_no_xss(value):
        if isinstance(value, str):
            lowered = value.lower()
            assert "<script" not in lowered and "onclick" not in lowered and "javascript:" not in lowered, "Possible XSS vulnerability in response data"

    def recursive_check(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                recursive_check(v)
        elif isinstance(obj, list):
            for item in obj:
                recursive_check(item)
        else:
            check_no_xss(obj)

    recursive_check(submit_json)


test_submit_quiz_answers_api()
