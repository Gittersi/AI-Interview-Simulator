from datetime import datetime
from typing import Optional, List

class User:
    def __init__(self, _id: str, email: str, name: str, password_hash: str, skills: List[str] = None):
        self._id = _id
        self.email = email
        self.name = name
        self.password_hash = password_hash
        self.skills = skills or []
        self.created_at = datetime.utcnow()

class Question:
    def __init__(self, _id: str, text: str, category: str, difficulty: str, timeLimit: int = 300):
        self._id = _id
        self.text = text
        self.category = category
        self.difficulty = difficulty
        self.timeLimit = timeLimit

class Answer:
    def __init__(self, questionId: str, text: Optional[str] = None, audioUrl: Optional[str] = None, code: Optional[str] = None):
        self.questionId = questionId
        self.text = text
        self.audioUrl = audioUrl
        self.code = code
        self.timestamp = datetime.utcnow()

class Interview:
    def __init__(self, _id: str, userId: str, status: str = "in_progress"):
        self._id = _id
        self.userId = userId
        self.startTime = datetime.utcnow()
        self.endTime = None
        self.status = status
        self.questions = []
        self.answers = []

class Evaluation:
    def __init__(self, answerId: str, correctness: float, confidence: float, communication: float, feedback: str):
        self.answerId = answerId
        self.correctness = correctness
        self.confidence = confidence
        self.communication = communication
        self.feedback = feedback

class PerformanceReport:
    def __init__(self, interviewId: str, evaluations: List[Evaluation]):
        self.interviewId = interviewId
        self.evaluations = evaluations
        self.timestamp = datetime.utcnow()
        self._calculate_scores()

    def _calculate_scores(self):
        if not self.evaluations:
            self.totalScore = 0
            self.correctnessScore = 0
            self.communicationScore = 0
            self.confidenceScore = 0
            self.suggestions = []
            return

        n = len(self.evaluations)
        self.correctnessScore = sum(e.correctness for e in self.evaluations) / n
        self.communicationScore = sum(e.communication for e in self.evaluations) / n
        self.confidenceScore = sum(e.confidence for e in self.evaluations) / n
        self.totalScore = (self.correctnessScore + self.communicationScore + self.confidenceScore) / 3

        self.suggestions = self._generate_suggestions()

    def _generate_suggestions(self):
        suggestions = []
        if self.correctnessScore < 70:
            suggestions.append("Focus on improving technical accuracy. Practice more problems in this category.")
        if self.communicationScore < 70:
            suggestions.append("Work on explaining your thoughts more clearly. Practice articulating your reasoning.")
        if self.confidenceScore < 70:
            suggestions.append("Build confidence by practicing similar questions multiple times.")
        if not suggestions:
            suggestions.append("Great performance! Keep practicing to maintain and improve your skills.")
        return suggestions
