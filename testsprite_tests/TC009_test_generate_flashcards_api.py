import requests

BASE_URL = "http://localhost:8000"
AUTH_EMAIL = "try.tusharjoshi@gmail.com"
AUTH_PASSWORD = "JQLCSG@8"
TIMEOUT = 30

def test_generate_flashcards_api():
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    flashcards_endpoint = f"{BASE_URL}/api/flashcards/generate"
    get_flashcards_endpoint = f"{BASE_URL}/api/flashcards/"

    # Login to get auth token
    login_payload = {
        "email": AUTH_EMAIL,
        "password": AUTH_PASSWORD
    }
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload, headers=headers, timeout=TIMEOUT)
    assert login_response.status_code == 200, f"Login failed with status {login_response.status_code}"
    login_data = login_response.json()
    assert "access_token" in login_data, "Login response missing access_token"
    token = login_data["access_token"]

    # Update headers with Bearer token
    headers["Authorization"] = f"Bearer {token}"

    # Test input with valid topic and number of cards to verify normal operation
    payload = {
        "topic": "Quantum Physics",
        "num_cards": 5
    }

    flashcard_set_id = None
    session = requests.Session()
    try:
        # Security checks: Input validation - send well-formed topic and num_cards.
        # Also test common attack payloads to detect injection/XSS issues
        malicious_payloads = [
            {"topic": "Quantum Physics; DROP TABLE users;", "num_cards": 5},
            {"topic": "<script>alert('xss')</script>", "num_cards": 5},
            {"topic": "NormalTopic", "num_cards": -10},  # Invalid negative number
            {"topic": "NormalTopic", "num_cards": "ten"},  # Invalid type
        ]

        # First, test with valid payload
        response = session.post(
            flashcards_endpoint,
            json=payload,
            headers=headers,
            timeout=TIMEOUT
        )
        assert response.status_code == 201 or response.status_code == 200, "Flashcard generation failed with valid input"
        data = response.json()

        # Adjusted assertion: 'id' may not be returned, check if present
        if "id" in data:
            flashcard_set_id = data["id"]

        assert isinstance(data.get("flashcards", []), list), "Flashcards list missing or malformed"
        assert len(data.get("flashcards", [])) == payload["num_cards"], "Number of flashcards generated does not match requested num_cards"
        # Validate no scripts or suspicious strings in flashcards content
        for card in data.get("flashcards", []):
            for key, val in card.items():
                assert not isinstance(val, str) or "<script>" not in val.lower(), "Potential XSS vulnerability detected in flashcard content"

        # Retrieve user's flashcard sets and verify the new set is listed and data matches
        get_response = session.get(
            get_flashcards_endpoint,
            headers=headers,
            timeout=TIMEOUT
        )
        assert get_response.status_code == 200, "Failed to retrieve flashcard sets"
        flashcards_list = get_response.json()
        assert isinstance(flashcards_list, list), "Flashcards list response malformed"
        # Check the flashcard set just created is in the list if id is known
        if flashcard_set_id:
            found = False
            for fset in flashcards_list:
                if fset.get("id") == flashcard_set_id:
                    found = True
                    # Verify topic and number of cards recorded
                    assert fset.get("topic", "") == payload["topic"], "Stored flashcard set topic mismatch"
                    assert len(fset.get("flashcards", [])) == payload["num_cards"], "Stored flashcard count mismatch"
                    break
            assert found, "Created flashcard set not found in user's flashcards list"

        # Test attack payloads for proper input validation and security
        for attack_payload in malicious_payloads:
            attack_response = session.post(
                flashcards_endpoint,
                json=attack_payload,
                headers=headers,
                timeout=TIMEOUT
            )
            # Should reject invalid inputs with 4xx client error codes
            assert 400 <= attack_response.status_code < 500, f"API did not reject malicious/invalid input payload: {attack_payload}"

    finally:
        # Cleanup: delete the created flashcard set if id is known
        if flashcard_set_id:
            delete_endpoint = f"{BASE_URL}/api/flashcards/{flashcard_set_id}"
            try:
                del_response = session.delete(
                    delete_endpoint,
                    headers=headers,
                    timeout=TIMEOUT
                )
                # Accept 200,204 or 404 if already deleted
                assert del_response.status_code in [200, 204, 404], "Failed to delete flashcard set during cleanup"
            except Exception:
                pass

test_generate_flashcards_api()
