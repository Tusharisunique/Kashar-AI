from utils.database import get_supabase_admin
from models.schemas import ProgressData
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ProgressService:
    def __init__(self):
        self.supabase = get_supabase_admin()
    
    async def get_user_progress(self, user_id: str, days: int = 30) -> ProgressData:
        """Get comprehensive progress data for a user"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get quiz scores
            quiz_scores = await self._get_quiz_scores(user_id, start_date, end_date)
            
            # Get tutor sessions
            tutor_sessions = await self._get_tutor_sessions(user_id, start_date, end_date)
            
            # Get topics studied
            topics_studied = await self._get_topics_studied(user_id, start_date, end_date)
            
            # Calculate total study time
            total_study_time = await self._calculate_total_study_time(user_id, start_date, end_date)
            
            progress_data = ProgressData(
                quiz_scores=quiz_scores,
                tutor_sessions=tutor_sessions,
                topics_studied=topics_studied,
                total_study_time=total_study_time
            )
            
            return progress_data
            
        except Exception as e:
            logger.error(f"Error getting user progress: {e}")
            raise
    
    async def _get_quiz_scores(self, user_id: str, start_date: datetime, end_date: datetime) -> list:
        """Get quiz scores within date range"""
        try:
            result = self.supabase.table("quiz_results").select("""
                score, total_questions, percentage, created_at,
                quizzes(topic, difficulty)
            """).eq("user_id", user_id).gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).order("created_at").execute()
            
            return result.data
        except Exception as e:
            logger.error(f"Error getting quiz scores: {e}")
            return []
    
    async def _get_tutor_sessions(self, user_id: str, start_date: datetime, end_date: datetime) -> list:
        """Get tutor sessions within date range"""
        try:
            result = self.supabase.table("tutor_sessions").select("*").eq("user_id", user_id).gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).order("created_at").execute()
            
            return result.data
        except Exception as e:
            logger.error(f"Error getting tutor sessions: {e}")
            return []
    
    async def _get_topics_studied(self, user_id: str, start_date: datetime, end_date: datetime) -> list:
        """Get unique topics studied within date range"""
        try:
            result = self.supabase.table("progress_logs").select("topic").eq("user_id", user_id).gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).execute()
            
            topics = list(set([log["topic"] for log in result.data if log["topic"]]))
            return topics
        except Exception as e:
            logger.error(f"Error getting topics studied: {e}")
            return []
    
    async def _calculate_total_study_time(self, user_id: str, start_date: datetime, end_date: datetime) -> int:
        """Calculate total study time in seconds"""
        try:
            result = self.supabase.table("progress_logs").select("duration").eq("user_id", user_id).gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).execute()
            
            total_time = sum([log["duration"] or 0 for log in result.data])
            return total_time
        except Exception as e:
            logger.error(f"Error calculating study time: {e}")
            return 0
    
    async def get_learning_streaks(self, user_id: str) -> dict:
        """Get learning streak information"""
        try:
            # Get activity for the last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            result = self.supabase.table("progress_logs").select("created_at").eq("user_id", user_id).gte("created_at", start_date.isoformat()).order("created_at", desc=True).execute()
            
            if not result.data:
                return {"current_streak": 0, "longest_streak": 0}
            
            # Calculate streaks
            activity_dates = set()
            for log in result.data:
                # Handle different datetime formats
                created_at = log["created_at"]
                if created_at.endswith('Z'):
                    created_at = created_at.replace('Z', '+00:00')
                
                # Handle microseconds that are too long (more than 6 digits)
                if '.' in created_at and '+' in created_at:
                    base_with_micro, timezone_part = created_at.rsplit('+', 1)
                    if '.' in base_with_micro:
                        base, microseconds = base_with_micro.split('.')
                        # Limit microseconds to 6 digits
                        microseconds = microseconds[:6].ljust(6, '0')
                        created_at = f"{base}.{microseconds}+{timezone_part}"
                
                try:
                    date = datetime.fromisoformat(created_at).date()
                    activity_dates.add(date)
                except ValueError as e:
                    logger.warning(f"Could not parse date {log['created_at']}: {e}")
                    continue
            
            current_streak = self._calculate_current_streak(activity_dates)
            longest_streak = self._calculate_longest_streak(activity_dates)
            
            return {
                "current_streak": current_streak,
                "longest_streak": longest_streak
            }
            
        except Exception as e:
            logger.error(f"Error getting learning streaks: {e}")
            return {"current_streak": 0, "longest_streak": 0}
    
    def _calculate_current_streak(self, activity_dates: set) -> int:
        """Calculate current learning streak"""
        if not activity_dates:
            return 0
        
        today = datetime.now().date()
        streak = 0
        current_date = today
        
        while current_date in activity_dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak
    
    def _calculate_longest_streak(self, activity_dates: set) -> int:
        """Calculate longest learning streak"""
        if not activity_dates:
            return 0
        
        sorted_dates = sorted(activity_dates)
        longest_streak = 1
        current_streak = 1
        
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1
        
        return longest_streak
    
    async def get_performance_analytics(self, user_id: str) -> dict:
        """Get performance analytics"""
        try:
            # Get quiz performance by topic
            quiz_result = self.supabase.table("quiz_results").select("""
                percentage, quizzes(topic, difficulty)
            """).eq("user_id", user_id).execute()
            
            # Calculate average scores by topic
            topic_performance = {}
            for result in quiz_result.data:
                topic = result["quizzes"]["topic"]
                percentage = result["percentage"]
                
                if topic not in topic_performance:
                    topic_performance[topic] = []
                topic_performance[topic].append(percentage)
            
            # Calculate averages
            topic_averages = {
                topic: sum(scores) / len(scores)
                for topic, scores in topic_performance.items()
            }
            
            # Get overall statistics
            total_quizzes = len(quiz_result.data)
            average_score = sum([r["percentage"] for r in quiz_result.data]) / total_quizzes if total_quizzes > 0 else 0
            
            return {
                "total_quizzes": total_quizzes,
                "average_score": round(average_score, 2),
                "topic_performance": topic_averages
            }
            
        except Exception as e:
            logger.error(f"Error getting performance analytics: {e}")
            return {"total_quizzes": 0, "average_score": 0, "topic_performance": {}}

progress_service = ProgressService()
