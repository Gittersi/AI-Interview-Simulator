"""
Answer Evaluator Module
Evaluates answers based on multiple criteria
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class AnswerEvaluator:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500)
    
    def evaluate(self, answer: str, reference: str = None, rubric: dict = None) -> dict:
        """
        Evaluate an answer against reference or rubric
        
        Args:
            answer: The user's answer
            reference: Expected/reference answer (optional)
            rubric: Evaluation rubric with criteria and weights
        
        Returns:
            Dictionary with evaluation scores
        """
        scores = {
            'completeness': self._evaluate_completeness(answer),
            'accuracy': self._evaluate_accuracy(answer, reference) if reference else 0,
            'clarity': self._evaluate_clarity(answer),
            'technical_depth': self._evaluate_technical_depth(answer)
        }
        
        # Calculate weighted total
        weights = rubric.get('weights', {}) if rubric else {}
        total_score = sum(
            scores.get(key, 0) * weights.get(key, 0.25)
            for key in ['completeness', 'accuracy', 'clarity', 'technical_depth']
        )
        
        scores['total'] = total_score
        return scores
    
    def _evaluate_completeness(self, answer: str) -> float:
        """Evaluate answer completeness based on length and structure"""
        words = answer.split()
        word_count = len(words)
        
        if word_count < 50:
            return 20.0
        elif word_count < 100:
            return 50.0
        elif word_count > 500:
            return 80.0
        else:
            return 90.0
    
    def _evaluate_accuracy(self, answer: str, reference: str) -> float:
        """Evaluate accuracy using semantic similarity"""
        try:
            corpus = [answer, reference]
            tfidf = self.vectorizer.fit_transform(corpus)
            similarity = cosine_similarity(tfidf[0], tfidf[1])[0][0]
            return float(similarity * 100)
        except:
            return 50.0
    
    def _evaluate_clarity(self, answer: str) -> float:
        """Evaluate clarity of explanation"""
        sentences = answer.split('.')
        avg_sentence_length = len(answer.split()) / max(len(sentences), 1)
        
        if avg_sentence_length < 5:
            return 70.0
        elif avg_sentence_length > 30:
            return 60.0
        else:
            return 85.0
    
    def _evaluate_technical_depth(self, answer: str) -> float:
        """Evaluate technical depth based on terminology"""
        technical_terms = [
            'algorithm', 'complexity', 'optimize', 'implement',
            'architecture', 'design', 'pattern', 'framework'
        ]
        
        answer_lower = answer.lower()
        term_count = sum(1 for term in technical_terms if term in answer_lower)
        
        return min(term_count * 15, 95.0)
