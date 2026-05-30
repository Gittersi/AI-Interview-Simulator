"""
NLP Utilities
Common NLP functions and helpers
"""

import re
from importlib import import_module
from collections import Counter

try:
    nltk = import_module('nltk')
    stopwords = import_module('nltk.corpus').stopwords
    tokenize = import_module('nltk.tokenize')
    sent_tokenize = tokenize.sent_tokenize
    word_tokenize = tokenize.word_tokenize
except ImportError:
    nltk = None
    stopwords = None
    sent_tokenize = None
    word_tokenize = None


_DEFAULT_STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has',
    'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was',
    'were', 'will', 'with', 'i', 'you', 'your', 'we', 'they', 'this', 'these',
    'those', 'or', 'but', 'if', 'then', 'than', 'so', 'because'
}


def _ensure_nltk_resource(resource_path: str, package_name: str) -> bool:
    """Return whether an NLTK resource is available without failing imports."""
    if nltk is None:
        return False

    try:
        nltk.data.find(resource_path)
        return True
    except LookupError:
        try:
            return bool(nltk.download(package_name, quiet=True))
        except Exception:
            return False

class NLPUtils:
    @staticmethod
    def tokenize_sentences(text: str) -> list:
        """Split text into sentences"""
        if _ensure_nltk_resource('tokenizers/punkt', 'punkt') and sent_tokenize:
            try:
                return sent_tokenize(text)
            except LookupError:
                pass

        return [sentence.strip() for sentence in re.split(r'(?<=[.!?])\s+', text) if sentence.strip()]
    
    @staticmethod
    def tokenize_words(text: str) -> list:
        """Split text into words"""
        if _ensure_nltk_resource('tokenizers/punkt', 'punkt') and word_tokenize:
            try:
                return word_tokenize(text.lower())
            except LookupError:
                pass

        return re.findall(r'\b\w+\b', text.lower())
    
    @staticmethod
    def remove_stopwords(words: list) -> list:
        """Remove common stopwords"""
        stop_words = _DEFAULT_STOPWORDS
        if _ensure_nltk_resource('corpora/stopwords', 'stopwords') and stopwords:
            try:
                stop_words = set(stopwords.words('english'))
            except LookupError:
                pass

        return [w for w in words if w.isalnum() and w not in stop_words]
    
    @staticmethod
    def extract_keywords(text: str, num_keywords: int = 10) -> list:
        """Extract important keywords from text"""
        words = NLPUtils.tokenize_words(text)
        keywords = NLPUtils.remove_stopwords(words)
        
        freq = Counter(keywords)
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
