"""
Sentiment and Confidence Analyzer
Analyzes sentiment and confidence in user responses
"""

from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import re

try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

class SentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
    
    def analyze(self, text: str) -> dict:
        """
        Analyze sentiment and extract confidence indicators
        
        Args:
            text: The text to analyze
        
        Returns:
            Dictionary with sentiment and confidence scores
        """
        # Sentiment analysis
        sentiments = self.sia.polarity_scores(text)
        
        # Confidence indicators
        confidence_features = self._extract_confidence_features(text)
        
        return {
            'sentiment': {
                'positive': sentiments['pos'],
                'negative': sentiments['neg'],
                'neutral': sentiments['neu'],
                'compound': sentiments['compound']
            },
            'confidence': {
                'score': self._calculate_confidence_score(text, sentiments),
                'certainty_level': self._get_certainty_level(text),
                'hesitation_indicators': confidence_features['hesitation'],
                'assertion_indicators': confidence_features['assertions']
            }
        }
    
    def _extract_confidence_features(self, text: str) -> dict:
        """Extract linguistic features related to confidence"""
        
        # Hesitation patterns
        hesitation_words = [
            r'\buh\b', r'\bum\b', r'\bmight\b', r'\bcould\b',
            r'\bmaybe\b', r'\bpossibly\b', r'\bi\s+think\b', r'\bi\s+guess\b'
        ]
        hesitation_count = sum(
            len(re.findall(pattern, text.lower()))
            for pattern in hesitation_words
        )
        
        # Assertion patterns
        assertion_words = [
            r'\bI\s+know\b', r'\bcertainly\b', r'\bdefinitely\b',
            r'\bsure\b', r'\bevidently\b', r'\bclearly\b'
        ]
        assertion_count = sum(
            len(re.findall(pattern, text.lower()))
            for pattern in assertion_words
        )
        
        return {
            'hesitation': hesitation_count,
            'assertions': assertion_count
        }
    
    def _calculate_confidence_score(self, text: str, sentiments: dict) -> float:
        """Calculate confidence score based on sentiment and features"""
        # Base score from sentiment compound (maps -1 to 1, to 0 to 100)
        sentiment_score = (sentiments['compound'] + 1) / 2 * 100
        
        # Adjust based on length (longer responses = more confidence)
        length_factor = min(len(text.split()) / 100, 1.0)
        
        # Combine
        confidence = sentiment_score * 0.7 + (length_factor * 100) * 0.3
        return min(confidence, 100.0)
    
    def _get_certainty_level(self, text: str) -> str:
        """Determine certainty level based on linguistic patterns"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['definitely', 'certainly', 'absolutely']):
            return 'high'
        elif any(word in text_lower for word in ['probably', 'likely', 'generally']):
            return 'medium'
        elif any(word in text_lower for word in ['maybe', 'possibly', 'might', 'could']):
            return 'low'
        else:
            return 'neutral'
