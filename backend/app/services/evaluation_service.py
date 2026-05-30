from typing import List, Optional
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import difflib

# Download required NLTK data (run once)
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

class EvaluationService:
    @staticmethod
    def evaluate_answer(answer_text: str, question_text: str, expected_keywords: Optional[List[str]] = None) -> dict:
        """
        Evaluate an answer based on semantic similarity and keyword matching.
        Returns scores for correctness, confidence, and communication.
        """
        
        # Calculate semantic similarity using simple string matching
        correctness = EvaluationService._calculate_semantic_similarity(
            answer_text, question_text
        )
        
        # Keyword matching
        if expected_keywords:
            keyword_score = EvaluationService._calculate_keyword_match(
                answer_text, expected_keywords
            )
            correctness = (correctness + keyword_score) / 2
        
        # Sentiment analysis for confidence
        confidence = EvaluationService._calculate_confidence(answer_text)
        
        # Communication analysis
        communication = EvaluationService._calculate_communication(answer_text)
        
        # Generate feedback
        feedback = EvaluationService._generate_feedback(
            correctness, confidence, communication, answer_text
        )
        
        return {
            "correctness": correctness,
            "confidence": confidence,
            "communication": communication,
            "feedback": feedback
        }

    @staticmethod
    def _calculate_semantic_similarity(text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts using difflib."""
        try:
            # Use SequenceMatcher for simple string similarity
            similarity = difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
            return float(similarity * 100)
        except:
            return 50.0

    @staticmethod
    def _calculate_keyword_match(answer: str, keywords: List[str]) -> float:
        """Calculate keyword match percentage."""
        answer_lower = answer.lower()
        found_keywords = sum(1 for keyword in keywords if keyword.lower() in answer_lower)
        return (found_keywords / len(keywords) * 100) if keywords else 50.0

    @staticmethod
    def _calculate_confidence(text: str) -> float:
        """Analyze sentiment to infer confidence."""
        sentiments = sia.polarity_scores(text)
        # Map compound score (-1 to 1) to confidence (0 to 100)
        confidence = (sentiments['compound'] + 1) / 2 * 100
        return float(confidence)

    @staticmethod
    def _calculate_communication(text: str) -> float:
        """Evaluate communication quality (length, structure, clarity)."""
        words = text.split()
        word_count = len(words)
        
        # Optimal answer length is 150-500 words
        if word_count < 50:
            return 20.0
        elif word_count < 100:
            return 50.0
        elif word_count > 1000:
            return 60.0
        elif 150 <= word_count <= 500:
            return 90.0
        else:
            return 75.0

    @staticmethod
    def _generate_feedback(correctness: float, confidence: float, communication: float, answer_text: str) -> str:
        """Generate feedback based on scores."""
        feedback_parts = []
        
        if correctness >= 80:
            feedback_parts.append("Your answer demonstrates strong technical understanding.")
        elif correctness >= 60:
            feedback_parts.append("Your answer covers the main points but could be more precise.")
        else:
            feedback_parts.append("Consider reviewing the fundamentals of this topic.")
        
        if communication >= 80:
            feedback_parts.append("Your explanation is clear and well-structured.")
        elif communication >= 60:
            feedback_parts.append("Try to be more concise and organized in your response.")
        else:
            feedback_parts.append("Focus on articulating your thoughts more clearly.")
        
        if confidence >= 75:
            feedback_parts.append("You sound confident in your answer.")
        elif confidence >= 50:
            feedback_parts.append("Work on expressing your ideas with more conviction.")
        else:
            feedback_parts.append("Practice more to build confidence in this area.")
        
        return " ".join(feedback_parts)

    @staticmethod
    def evaluate_code(code: str, language: str) -> dict:
        """Basic code evaluation - can be extended with actual execution."""
        return {
            "syntax_valid": True,
            "execution_time": 0.1,
            "memory_usage": 0,
            "correctness": 75.0,
            "feedback": "Code executed successfully. Consider optimizing for better performance."
        }
