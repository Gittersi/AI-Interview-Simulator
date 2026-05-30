from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DifficultyEnum(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class InterviewStatusEnum(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

# User Schema
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    skills: List[str] = []

    class Config:
        from_attributes = True

# Question Schema
class QuestionCreate(BaseModel):
    text: str
    category: str
    difficulty: DifficultyEnum
    timeLimit: int = 300

class QuestionResponse(BaseModel):
    id: str
    text: str
    category: str
    difficulty: DifficultyEnum
    timeLimit: int

# Interview Schema
class AnswerCreate(BaseModel):
    questionId: Optional[str] = None
    text: Optional[str] = None
    audioUrl: Optional[str] = None
    code: Optional[str] = None

class AnswerResponse(BaseModel):
    questionId: str
    text: Optional[str]
    audioUrl: Optional[str]
    code: Optional[str]
    timestamp: datetime

class InterviewCreate(BaseModel):
    difficulty: DifficultyEnum
    category: str

class ResumeTextCreate(BaseModel):
    resumeText: str = Field(..., min_length=20)

class ResumeUpdateCreate(ResumeTextCreate):
    jobDescription: str = Field(..., min_length=20)

class ResumeInterviewCreate(ResumeTextCreate):
    difficulty: DifficultyEnum = DifficultyEnum.MEDIUM

class InterviewResponse(BaseModel):
    id: str
    userId: str
    startTime: datetime
    endTime: Optional[datetime] = None
    status: InterviewStatusEnum
    questionCount: int = 0
    category: Optional[str] = None
    difficulty: Optional[DifficultyEnum] = None
    questions: List[QuestionResponse] = []

# Evaluation Schema
class EvaluationResponse(BaseModel):
    answerId: str
    correctness: float
    confidence: float
    communication: float
    feedback: str

class PerformanceReportResponse(BaseModel):
    interviewId: str
    totalScore: float
    correctnessScore: float
    communicationScore: float
    confidenceScore: float
    evaluations: List[EvaluationResponse]
    suggestions: List[str]
    timestamp: datetime

# Token Schema
class TokenResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    user: UserResponse
