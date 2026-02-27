"""
Chat&Talk GPT - Trivia Quiz
Quiz system using Open Trivia Database API
"""
import json
import logging
import urllib.request
import urllib.parse
import urllib.error
import uuid
import html
from typing import Dict, Any, List, Optional

logger = logging.getLogger("TriviaQuiz")

# Open Trivia DB API base URL
TRIVIA_API_BASE = "https://opentdb.com"


class TriviaQuiz:
    """
    Trivia quiz system using Open Trivia Database API
    Features:
    - Get questions by category and difficulty
    - Multiple choice questions
    - Answer checking
    - Category listing
    """
    
    # API endpoints
    API_CATEGORIES = f"{TRIVIA_API_BASE}/api_category.php"
    API_QUESTIONS = f"{TRIVIA_API_BASE}/api.php"
    API_TOKEN = f"{TRIVIA_API_BASE}/api_token.php"
    
    # Valid difficulties
    VALID_DIFFICULTIES = ["easy", "medium", "hard"]
    
    # Question type
    QUESTION_TYPE = "multiple"
    
    def __init__(self):
        """Initialize trivia quiz"""
        self._session_token = None
        self._current_questions = []
        logger.info("TriviaQuiz initialized")
    
    def _make_request(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request to API
        
        Args:
            url: Full URL to request
        
        Returns:
            JSON response as dictionary
        """
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data
        except urllib.error.URLError as e:
            logger.error(f"API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response: {e}")
            return None
    
    def _get_session_token(self) -> Optional[str]:
        """
        Get a session token to prevent duplicate questions
        
        Returns:
            Session token string or None
        """
        if self._session_token:
            return self._session_token
        
        try:
            url = f"{self.API_TOKEN}?command=request"
            data = self._make_request(url)
            
            if data and data.get("response_code") == 0:
                self._session_token = data.get("token")
                logger.info("Got new session token")
                return self._session_token
        except Exception as e:
            logger.error(f"Failed to get session token: {e}")
        
        return None
    
    def _reset_token(self):
        """Reset the session token"""
        if self._session_token:
            try:
                url = f"{self.API_TOKEN}?command=reset&token={self._session_token}"
                self._make_request(url)
                logger.info("Session token reset")
            except Exception as e:
                logger.error(f"Failed to reset token: {e}")
            finally:
                self._session_token = None
    
    def _decode_html(self, text: str) -> str:
        """
        Decode HTML entities in text
        
        Args:
            text: Text with HTML entities
        
        Returns:
            Decoded text
        """
        return html.unescape(text)
    
    def _create_question(self, api_question: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        Transform API question to our format
        
        Args:
            api_question: Raw question from API
            index: Question index number
        
        Returns:
            Formatted question
        """
        # Get incorrect answers and correct answer
        incorrect_answers = api_question.get("incorrect_answers", [])
        correct_answer = api_question.get("correct_answer", "")
        
        # Combine and shuffle answers
        all_answers = incorrect_answers + [correct_answer]
        # Note: The API doesn't guarantee shuffled order, so we shuffle ourselves
        import random
        random.shuffle(all_answers)
        
        return {
            "id": str(uuid.uuid4())[:8],
            "index": index,
            "category": self._decode_html(api_question.get("category", "")),
            "difficulty": api_question.get("difficulty", "medium"),
            "type": api_question.get("type", "multiple"),
            "question": self._decode_html(api_question.get("question", "")),
            "correct_answer": self._decode_html(correct_answer),
            "all_answers": [self._decode_html(a) for a in all_answers],
            "user_answer": None,
            "is_correct": None
        }
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get available trivia categories
        
        Returns:
            List of category dictionaries with id and name
        """
        data = self._make_request(self.API_CATEGORIES)
        
        if data and data.get("trivia_categories"):
            categories = data["trivia_categories"]
            logger.info(f"Retrieved {len(categories)} categories")
            return categories
        
        # Return common categories as fallback
        logger.warning("Using fallback categories")
        return [
            {"id": 9, "name": "General Knowledge"},
            {"id": 10, "name": "Entertainment: Books"},
            {"id": 11, "name": "Entertainment: Film"},
            {"id": 12, "name": "Entertainment: Music"},
            {"id": 14, "name": "Entertainment: Television"},
            {"id": 15, "name": "Entertainment: Video Games"},
            {"id": 17, "name": "Science & Nature"},
            {"id": 18, "name": "Science: Computers"},
            {"id": 19, "name": "Science: Mathematics"},
            {"id": 21, "name": "Sports"},
            {"id": 22, "name": "Geography"},
            {"id": 23, "name": "History"},
            {"id": 27, "name": "Animals"}
        ]
    
    def get_questions(
        self,
        category: int = None,
        difficulty: str = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get trivia questions
        
        Args:
            category: Category ID (None for any category)
            difficulty: "easy", "medium", or "hard" (None for any)
            limit: Number of questions (max 50)
        
        Returns:
            Dictionary with questions array
        """
        # Validate limit
        limit = min(max(1, limit), 50)
        
        # Validate difficulty
        if difficulty and difficulty.lower() not in self.VALID_DIFFICULTIES:
            difficulty = None
        
        # Build API URL
        params = {
            "amount": limit,
            "type": self.QUESTION_TYPE
        }
        
        if category:
            params["category"] = category
        
        if difficulty:
            params["difficulty"] = difficulty.lower()
        
        # Add session token
        token = self._get_session_token()
        if token:
            params["token"] = token
        
        url = f"{self.API_QUESTIONS}?{urllib.parse.urlencode(params)}"
        
        # Make request
        data = self._make_request(url)
        
        if not data:
            return {
                "success": False,
                "error": "Failed to fetch questions",
                "questions": []
            }
        
        response_code = data.get("response_code", -1)
        
        # Handle response codes
        if response_code == 0:
            # Success
            questions = [
                self._create_question(q, i)
                for i, q in enumerate(data.get("results", []))
            ]
            
            # Store current questions for answer checking
            self._current_questions = questions
            
            logger.info(f"Retrieved {len(questions)} questions")
            
            return {
                "success": True,
                "questions": questions,
                "category": category,
                "difficulty": difficulty
            }
        
        elif response_code == 1:
            # Not enough questions available
            error_msg = "Not enough questions available for this category/difficulty"
            logger.warning(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "questions": []
            }
        
        elif response_code == 2:
            # Invalid parameter
            return {
                "success": False,
                "error": "Invalid parameter",
                "questions": []
            }
        
        elif response_code == 3:
            # Token not found - reset and try again
            self._reset_token()
            return self.get_questions(category, difficulty, limit)
        
        elif response_code == 4:
            # Token exhausted - reset and try again
            self._reset_token()
            return self.get_questions(category, difficulty, limit)
        
        else:
            return {
                "success": False,
                "error": f"Unknown error (code: {response_code})",
                "questions": []
            }
    
    def check_answer(self, question_id: str, user_answer: str) -> Dict[str, Any]:
        """
        Check if user's answer is correct
        
        Args:
            question_id: ID of the question
            user_answer: User's answer string
        
        Returns:
            Dictionary with result
        """
        # Find the question
        question = None
        for q in self._current_questions:
            if q.get("id") == question_id:
                question = q
                break
        
        if not question:
            return {
                "correct": False,
                "error": "Question not found",
                "correct_answer": None
            }
        
        # Check answer (case-insensitive)
        is_correct = user_answer.strip().lower() == question["correct_answer"].strip().lower()
        
        # Update question with user's answer
        question["user_answer"] = user_answer
        question["is_correct"] = is_correct
        
        logger.info(f"Answer checked for question {question_id}: {is_correct}")
        
        return {
            "correct": is_correct,
            "correct_answer": question["correct_answer"],
            "question": question["question"]
        }
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get results for current question set
        
        Returns:
            Dictionary with results summary
        """
        if not self._current_questions:
            return {
                "total": 0,
                "correct": 0,
                "incorrect": 0,
                "accuracy": 0
            }
        
        correct = sum(1 for q in self._current_questions if q.get("is_correct") is True)
        total = len(self._current_questions)
        
        return {
            "total": total,
            "correct": correct,
            "incorrect": total - correct,
            "accuracy": round((correct / total) * 100, 1) if total > 0 else 0
        }
    
    def get_category_name(self, category_id: int) -> str:
        """
        Get category name by ID
        
        Args:
            category_id: Category ID
        
        Returns:
            Category name
        """
        categories = self.get_categories()
        for cat in categories:
            if cat.get("id") == category_id:
                return cat.get("name", "Unknown")
        return "Unknown"


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    quiz = TriviaQuiz()
    
    # Test getting categories
    print("Available categories:")
    categories = quiz.get_categories()
    for cat in categories[:5]:
        print(f"  - {cat['name']} (ID: {cat['id']})")
    
    # Test getting questions
    print("\nGetting 5 easy questions...")
    result = quiz.get_questions(difficulty="easy", limit=5)
    
    if result.get("success"):
        print(f"Got {len(result['questions'])} questions!")
        for q in result["questions"][:2]:
            print(f"\nQ: {q['question']}")
            print(f"Answers: {q['all_answers']}")
            print(f"Correct: {q['correct_answer']}")
    else:
        print(f"Error: {result.get('error')}")
    
    # Test answer checking
    if result.get("questions"):
        q_id = result["questions"][0]["id"]
        correct_ans = result["questions"][0]["correct_answer"]
        check = quiz.check_answer(q_id, correct_ans)
        print(f"\nAnswer check: {check}")
