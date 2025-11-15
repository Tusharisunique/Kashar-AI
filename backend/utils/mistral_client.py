import requests
from utils.config import OPENROUTER_API_KEY
import logging

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        self.embedding_model = "text-embedding-3-small"  # OpenAI embedding model via OpenRouter
        self.chat_model = "openai/gpt-3.5-turbo"  # GPT-3.5 Turbo via OpenRouter
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",  # Optional: for OpenRouter analytics
            "X-Title": "Kashar AI"  # Optional: for OpenRouter analytics
        }
    
    async def generate_embeddings(self, texts: list) -> list:
        """Generate embeddings for a list of texts"""
        try:
            payload = {
                "model": self.embedding_model,
                "input": texts
            }
            
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return [embedding["embedding"] for embedding in result["data"]]
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    async def chat_completion(self, messages: list, max_tokens: int = 1000) -> str:
        """Generate chat completion"""
        try:
            payload = {
                "model": self.chat_model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise
    
    async def generate_quiz_questions(self, context: str, topic: str, difficulty: str, num_questions: int = 5) -> list:
        """Generate quiz questions based on context"""
        prompt = f"""Based on the following study material about {topic}, create {num_questions} multiple choice questions at {difficulty} difficulty level.

Study Material:
{context}

Format each question as JSON with:
- "question": the question text
- "options": array of 4 options
- "correct_answer": index (0-3) of correct option

Return only a JSON array of questions, no additional text."""

        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.chat_completion(messages, max_tokens=1500)
            
            # Parse JSON response
            import json
            questions = json.loads(response)
            return questions
        except Exception as e:
            logger.error(f"Error generating quiz questions: {e}")
            raise
    
    async def generate_flashcards(self, context: str, topic: str, num_cards: int = 10) -> list:
        """Generate flashcards based on context"""
        prompt = f"""Based on the following study material about {topic}, create {num_cards} flashcards.

Study Material:
{context}

Format each flashcard as JSON with:
- "question": the question or prompt
- "answer": the answer or explanation

Return only a JSON array of flashcards, no additional text."""

        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.chat_completion(messages, max_tokens=1500)
            
            # Parse JSON response
            import json
            flashcards = json.loads(response)
            return flashcards
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            raise

# Global AI client instance
ai_client = AIClient()
