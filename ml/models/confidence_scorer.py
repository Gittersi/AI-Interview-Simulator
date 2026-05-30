"""
Confidence Scoring Module
Analyzes and scores confidence levels in responses
"""

import re
from collections import Counter

class ConfidenceScorer:
    """Score confidence based on various linguistic and structural features"""
    
    POSITIVE_CONFIDENCE_WORDS = {
        'sure': 0.9, 'certainly': 0.95, 'absolutely': 0.95,
        'definitely': 0.9, 'clearly': 0.8, 'obviously': 0.8,
        'always': 0.85, 'never': 0.85, 'definitely': 0.9
    }
    
    NEGATIVE_CONFIDENCE_WORDS = {
        'maybe': 0.3, 'might': 0.4, 'could': 0.45,
        'possibly': 0.35, 'probably': 0.55, 'likely': 0.6,
        'i think': 0.5, 'i guess': 0.4, 'perhaps': 0.35
    }
    
    def score(self, text: str) -> dict:
        """
        Calculate comprehensive confidence score
        
        Returns:
            Dictionary with confidence metrics
        """
        
        # Extract metrics
        linguistic_score = self._score_linguistic_patterns(text)
        structural_score = self._score_text_structure(text)
        vocabulary_score = self._score_vocabulary(text)
        
        # Weighted combination
        overall_confidence = (
            linguistic_score * 0.4 +
            structural_score * 0.35 +
            vocabulary_score * 0.25
        )
        
        return {
            'overall': min(overall_confidence, 100.0),
            'linguistic': linguistic_score,
            'structural': structural_score,
            'vocabulary': vocabulary_score,
            'level': self._get_confidence_level(overall_confidence)
        }
    
    def _score_linguistic_patterns(self, text: str) -> float:
        """Score based on confidence-related word patterns"""
        text_lower = text.lower()
        
        positive_score = 0
        for word, weight in self.POSITIVE_CONFIDENCE_WORDS.items():
            if word in text_lower:
                positive_score += weight
        
        negative_score = 0
        for word, weight in self.NEGATIVE_CONFIDENCE_WORDS.items():
            if word in text_lower:
                negative_score += weight
        
        # Normalize
        total_words = len(text.split())
        if total_words == 0:
            return 50.0
        
        confidence = (positive_score - negative_score) / max(total_words, 1) * 100
        return max(min(confidence + 50, 100.0), 0.0)
    
    def _score_text_structure(self, text: str) -> float:
        """Score based on text organization and structure"""
        sentences = text.split('.')
        paragraphs = text.split('\n\n')
        
        # Well-structured text shows confidence
        structure_score = 50.0
        
        if len(sentences) > 2:
            structure_score += 15
        if len(paragraphs) > 1:
            structure_score += 15
        
        # Check for examples or evidence
        if any(phrase in text.lower() for phrase in ['for example', 'such as', 'evidence', 'specifically']):
            structure_score += 20
        
        return min(structure_score, 100.0)
    
    def _score_vocabulary(self, text: str) -> float:
        """Score based on vocabulary sophistication"""
        technical_terms = [
            'algorithm', 'optimize', 'implement', 'architecture',
            'pattern', 'framework', 'complexity', 'efficiency',
            'scalable', 'robust', 'performance', 'analysis'
        ]
        
        text_lower = text.lower()
        term_count = sum(1 for term in technical_terms if term in text_lower)
        
        vocab_score = min((term_count / 5) * 100, 90.0)
        
        # Add base score
        vocab_score += 10
        
        return min(vocab_score, 100.0)
    
    def _get_confidence_level(self, score: float) -> str:
        """Categorize confidence level"""
        if score >= 80:
            return 'Very High'
        elif score >= 60:
            return 'High'
        elif score >= 40:
            return 'Medium'
        elif score >= 20:
            return 'Low'
        else:
            return 'Very Low'
