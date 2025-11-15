import uuid
from utils.database import get_supabase_admin
from utils.chroma_client import chroma_client
from utils.mistral_client import ai_client
from models.schemas import QuizRequest, QuizSubmission, Quiz, QuizResult
import logging

logger = logging.getLogger(__name__)

class QuizService:
    def __init__(self):
        self.supabase = get_supabase_admin()
    
    async def generate_quiz(self, quiz_request: QuizRequest, user_id: str) -> Quiz:
        """Generate a quiz based on topic and difficulty"""
        try:
            # Get relevant chunks from ChromaDB
            query_embedding = await ai_client.generate_embeddings([quiz_request.topic])
            
            results = chroma_client.query_documents(
                query_embeddings=query_embedding,
                n_results=10,
                where={"user_id": user_id}
            )
            
            if not results['documents'][0]:
                raise Exception(f"No study material found for topic: {quiz_request.topic}")
            
            # Combine relevant chunks
            context = "\n\n".join(results['documents'][0])
            
            # Generate questions using LLM
            questions = await ai_client.generate_quiz_questions(
                context=context,
                topic=quiz_request.topic,
                difficulty=quiz_request.difficulty,
                num_questions=quiz_request.num_questions
            )
            
            # Create quiz record
            quiz_id = str(uuid.uuid4())
            quiz_record = {
                "id": quiz_id,
                "user_id": user_id,
                "topic": quiz_request.topic,
                "difficulty": quiz_request.difficulty,
                "questions": questions
            }
            
            self.supabase.table("quizzes").insert(quiz_record).execute()
            
            quiz = Quiz(
                id=quiz_id,
                questions=questions,
                topic=quiz_request.topic,
                difficulty=quiz_request.difficulty
            )
            
            logger.info(f"Quiz generated for user {user_id}, topic: {quiz_request.topic}")
            return quiz
            
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            raise
    
    async def submit_quiz(self, submission: QuizSubmission, user_id: str) -> QuizResult:
        """Submit quiz answers and calculate score"""
        try:
            # Get quiz from database
            quiz_result = self.supabase.table("quizzes").select("*").eq("id", submission.quiz_id).eq("user_id", user_id).execute()
            
            if not quiz_result.data:
                raise Exception("Quiz not found")
            
            quiz_data = quiz_result.data[0]
            questions = quiz_data["questions"]
            
            # Calculate score
            correct_answers = 0
            total_questions = len(questions)
            
            for i, user_answer in enumerate(submission.answers):
                if i < len(questions) and user_answer == questions[i]["correct_answer"]:
                    correct_answers += 1
            
            percentage = (correct_answers / total_questions) * 100
            
            # Determine new difficulty level
            new_difficulty = self._calculate_new_difficulty(percentage, quiz_data["difficulty"])
            
            # Store quiz result
            result_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "quiz_id": submission.quiz_id,
                "score": correct_answers,
                "total_questions": total_questions,
                "percentage": percentage,
                "answers": submission.answers
            }
            
            self.supabase.table("quiz_results").insert(result_record).execute()
            
            # Log progress
            progress_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "activity_type": "quiz",
                "topic": quiz_data["topic"],
                "score": correct_answers,
                "metadata": {
                    "quiz_id": submission.quiz_id,
                    "difficulty": quiz_data["difficulty"],
                    "percentage": percentage
                }
            }
            
            self.supabase.table("progress_logs").insert(progress_record).execute()
            
            result = QuizResult(
                quiz_id=submission.quiz_id,
                score=correct_answers,
                total_questions=total_questions,
                percentage=percentage,
                new_difficulty=new_difficulty
            )
            
            logger.info(f"Quiz submitted for user {user_id}, score: {correct_answers}/{total_questions}")
            return result
            
        except Exception as e:
            logger.error(f"Error submitting quiz: {e}")
            raise
    
    def _calculate_new_difficulty(self, percentage: float, current_difficulty: str) -> str:
        """Calculate new difficulty based on performance"""
        if percentage >= 80:
            if current_difficulty == "easy":
                return "medium"
            elif current_difficulty == "medium":
                return "hard"
            else:
                return "hard"
        elif percentage >= 50:
            return current_difficulty
        else:
            if current_difficulty == "hard":
                return "medium"
            elif current_difficulty == "medium":
                return "easy"
            else:
                return "easy"
    
    async def get_user_quiz_history(self, user_id: str) -> list:
        """Get quiz history for user"""
        try:
            result = self.supabase.table("quiz_results").select("""
                *, quizzes(topic, difficulty, created_at)
            """).eq("user_id", user_id).order("created_at", desc=True).execute()
            
            return result.data
        except Exception as e:
            logger.error(f"Error getting quiz history: {e}")
            raise

quiz_service = QuizService()
