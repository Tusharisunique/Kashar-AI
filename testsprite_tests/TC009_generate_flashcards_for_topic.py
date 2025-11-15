import requests
from requests.auth import HTTPBasicAuth


BASE_URL = "http://localhost:3000"
AUTH = HTTPBasicAuth("try.tusharjoshi@gmail.com", "JQLCSG@8")
TIMEOUT = 30


def test_generate_flashcards_for_topic():
    """
    Verify flashcard generation at /api/flashcards/generate for given topics and number of cards,
    ensuring relevant flashcards are created.
    """
    url_generate = f"{BASE_URL}/api/flashcards/generate"
    url_get_flashcards = f"{BASE_URL}/api/flashcards/"

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "topic": "machine learning",
        "num_cards": 5
    }

    # Create flashcards for the topic
    response = requests.post(url_generate, json=payload, headers=headers, auth=AUTH, timeout=TIMEOUT)
    try:
        assert response.status_code == 201 or response.status_code == 200, f"Expected 201/200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "Response JSON is not a dict"
        # Validate expected keys in response (for example: flashcards list, topic, num_cards)
        assert "flashcards" in data, "Response missing 'flashcards' key"
        assert isinstance(data["flashcards"], list), "'flashcards' is not a list"
        assert len(data["flashcards"]) == payload["num_cards"], f"Expected {payload['num_cards']} flashcards, got {len(data['flashcards'])}"

        # Optionally check flashcard content relevance (non-empty content)
        for card in data["flashcards"]:
            assert isinstance(card, dict), "Flashcard item is not a dict"
            assert "question" in card, "Flashcard missing 'question'"
            assert "answer" in card, "Flashcard missing 'answer'"
            assert isinstance(card["question"], str) and card["question"], "Flashcard 'question' empty or not a string"
            assert isinstance(card["answer"], str) and card["answer"], "Flashcard 'answer' empty or not a string"

        # Fetch all flashcard sets for the user and confirm the generated flashcards are present
        get_resp = requests.get(url_get_flashcards, headers=headers, auth=AUTH, timeout=TIMEOUT)
        assert get_resp.status_code == 200, f"Expected 200 on flashcards retrieval, got {get_resp.status_code}"
        flashcards_data = get_resp.json()
        assert isinstance(flashcards_data, list), "Flashcards GET response is not a list"

        # Check that at least one flashcard set includes the topic flashcards
        matching_sets = [fs for fs in flashcards_data if "topic" in fs and fs["topic"] == payload["topic"]]
        assert matching_sets, f"No flashcard set found for topic '{payload['topic']}'"

        # Confirm that the flashcards in the matching set correspond to those generated
        found_cards = []
        for fs in matching_sets:
            if "flashcards" in fs and isinstance(fs["flashcards"], list):
                found_cards.extend(fs["flashcards"])
        assert len(found_cards) >= payload["num_cards"], f"Expected at least {payload['num_cards']} cards in user's flashcards, got {len(found_cards)}"

    except (AssertionError, requests.RequestException) as e:
        raise
    finally:
        # Clean up: If the API supported flashcard deletion by topic or ID, it would be performed here.
        # The PRD does not specify deletion endpoints for flashcards; hence no cleanup is performed.
        pass


test_generate_flashcards_for_topic()