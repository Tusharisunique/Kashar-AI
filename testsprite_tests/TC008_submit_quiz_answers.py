import requests

BASE_URL = "http://localhost:3000"
AUTH_EMAIL = "try.tusharjoshi@gmail.com"
AUTH_PASSWORD = "JQLCSG@8"
TIMEOUT = 30

def test_submit_quiz_answers():
    headers = {
        "Content-Type": "application/json"
    }

    # Step 0: Login to get auth token (or session cookie)
    login_url = f"{BASE_URL}/api/auth/login"
    login_payload = {
        "email": AUTH_EMAIL,
        "password": AUTH_PASSWORD
    }
    response_login = requests.post(login_url, json=login_payload, headers=headers, timeout=TIMEOUT)
    assert response_login.status_code == 200, f"Login failed: {response_login.text}"
    login_data = response_login.json()

    # Assuming token key is 'access_token' - if not present, fallback to no auth header
    token = login_data.get("access_token")

    auth_headers = headers.copy()
    if token:
        auth_headers["Authorization"] = f"Bearer {token}"

    # Step 1: Generate a quiz first to get a valid quiz_id and number of questions
    generate_quiz_url = f"{BASE_URL}/api/quiz/generate"
    generate_payload = {
        "topic": "sample topic",
        "difficulty": "easy",
        "num_questions": 3
    }

    response_generate = requests.post(generate_quiz_url, json=generate_payload, headers=auth_headers, timeout=TIMEOUT)
    assert response_generate.status_code == 200, f"Quiz generation failed: {response_generate.text}"
    quiz_data = response_generate.json()
    # Expecting quiz_data to contain quiz_id and questions
    assert "quiz_id" in quiz_data and isinstance(quiz_data["quiz_id"], str), "quiz_id missing or invalid in quiz generation response"
    assert "questions" in quiz_data and isinstance(quiz_data["questions"], list), "questions missing or invalid in quiz generation response"
    assert len(quiz_data["questions"]) == generate_payload["num_questions"], "Number of questions mismatch in quiz generation"

    quiz_id = quiz_data["quiz_id"]
    questions = quiz_data["questions"]

    # Step 2: Prepare answers - for testing, submit answer as 0 for all questions (assuming answers are integer indices)
    answers = []
    for q in questions:
        answers.append(0)

    submit_url = f"{BASE_URL}/api/quiz/submit"
    submit_payload = {
        "quiz_id": quiz_id,
        "answers": answers
    }

    try:
        response_submit = requests.post(submit_url, json=submit_payload, headers=auth_headers, timeout=TIMEOUT)
        assert response_submit.status_code == 200, f"Quiz submission failed: {response_submit.text}"
        submit_response = response_submit.json()

        # Validate response contains expected confirmation or updated progress fields
        # Since PRD doesn't specify exact response schema for submit, validate minimal:
        assert "status" in submit_response or "message" in submit_response or "progress" in submit_response, \
            "Response from quiz submit endpoint missing expected keys"

        # Step 3: Check progress tracking updated by calling progress API (optional but validating core functionality)
        progress_url = f"{BASE_URL}/api/progress/"
        response_progress = requests.get(progress_url, headers=auth_headers, timeout=TIMEOUT)
        assert response_progress.status_code == 200, f"Failed to retrieve progress data after quiz submission: {response_progress.text}"
        progress_data = response_progress.json()

        # Expect progress data to be a dict with some tracking info (like quiz scores or streaks)
        assert isinstance(progress_data, dict), "Progress data is not a dictionary"
        assert any(key in progress_data for key in ("quiz_scores", "accuracy", "streaks", "time_spent")), \
            "Progress data missing expected tracking keys"

    finally:
        pass

test_submit_quiz_answers()
