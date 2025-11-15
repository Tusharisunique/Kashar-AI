import requests

BASE_URL = "http://localhost:3000"
TIMEOUT = 30

def test_generate_quiz_for_topic():
    url = f"{BASE_URL}/api/quiz/generate"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    test_cases = [
        {"topic": "Mathematics", "difficulty": "easy", "num_questions": 5},
        {"topic": "Physics", "difficulty": "medium", "num_questions": 10},
        {"topic": "History", "difficulty": "hard", "num_questions": 15},
        {"topic": "Biology", "difficulty": "easy", "num_questions": 1},
        {"topic": "Chemistry", "difficulty": "medium", "num_questions": 20}
    ]

    for case in test_cases:
        payload = {
            "topic": case["topic"],
            "difficulty": case["difficulty"],
            "num_questions": case["num_questions"]
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"Request to generate quiz failed for case {case} with error: {e}"

        assert response.status_code == 200, f"Expected status 200 but got {response.status_code} for case {case}"

        try:
            data = response.json()
        except ValueError:
            assert False, f"Response is not valid JSON for case {case}"

        assert "quiz_id" in data, f"Response missing 'quiz_id' for case {case}"
        assert "topic" in data, f"Response missing 'topic' for case {case}"
        assert data["topic"].lower() == case["topic"].lower(), f"Returned topic mismatch for case {case}"
        assert "difficulty" in data, f"Response missing 'difficulty' for case {case}"
        assert data["difficulty"] == case["difficulty"], f"Returned difficulty mismatch for case {case}"
        assert "questions" in data, f"Response missing 'questions' for case {case}"
        questions = data["questions"]
        assert isinstance(questions, list), f"'questions' is not a list for case {case}"
        assert len(questions) == case["num_questions"], f"Number of questions mismatch for case {case}"

        for q in questions:
            assert isinstance(q, dict), f"Question item is not a dictionary for case {case}"
            assert "question_text" in q, f"Question missing 'question_text' for case {case}"
            assert isinstance(q["question_text"], str) and q["question_text"].strip(), f"Invalid 'question_text' for case {case}"
            assert "type" in q, f"Question missing 'type' field for case {case}"
            assert q["type"] in ["MCQ", "True/False", "Short Answer", "Multiple Choice"], f"Unexpected question type '{q['type']}' for case {case}"

test_generate_quiz_for_topic()
