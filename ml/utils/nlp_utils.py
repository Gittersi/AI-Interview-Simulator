"""
NLP Utilities
Common NLP functions and helpers
"""

import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('stopwords')
except LookupError:
    nltk.download('stopwords')

class NLPUtils:
    @staticmethod
    def tokenize_sentences(text: str) -> list:
        """Split text into sentences"""
        return sent_tokenize(text)
    
    @staticmethod
    def tokenize_words(text: str) -> list:
        """Split text into words"""
        return word_tokenize(text.lower())
    
    @staticmethod
    def remove_stopwords(words: list) -> list:
        """Remove common stopwords"""
        stop_words = set(stopwords.words('english'))
        return [w for w in words if w.isalnum() and w not in stop_words]
    
    @staticmethod
    def extract_keywords(text: str, num_keywords: int = 10) -> list:
        """Extract important keywords from text"""
        words = NLPUtils.tokenize_words(text)
        keywords = NLPUtils.remove_stopwords(words)
        
        # Count frequency
        freq = nltk.FreqDist(keywords)
        
        # Return top keywords
        return [word for word, _ in freq.most_common(num_keywords)]
    
    @staticmethod
    def calculate_text_metrics(text: str) -> dict:
        """Calculate various text metrics"""
        sentences = NLPUtils.tokenize_sentences(text)
        words = NLPUtils.tokenize_words(text)
        unique_words = set(words)
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'unique_words': len(unique_words),
            'avg_sentence_length': len(words) / max(len(sentences), 1),
            'avg_word_length': sum(len(w) for w in words) / max(len(words), 1),
            'lexical_diversity': len(unique_words) / len(words) if words else 0
        }
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters (keep alphanumeric, spaces, punctuation)
        text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
        return text.strip()
