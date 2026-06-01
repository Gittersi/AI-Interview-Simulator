from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.schemas import (
    QuestionResponse,
    QuestionGenerationCreate,
    ResumeQuestionGenerateCreate,
    DifficultyEnum,
)
from app.services.auth_service import AuthService
from app.services.llm_service import LLMService
from app.services.resume_parser_service import ResumeParserService
from app.db.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/questions", tags=["questions"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
    user_id = AuthService.decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return user_id


@router.post("/random", response_model=list[QuestionResponse])
async def generate_random_questions(
    request: QuestionGenerationCreate,
    user_id: str = Depends(get_current_user),
):
    """Generate a set of interview questions using an LLM."""
    questions = LLMService.generate_questions(
        request.category,
        request.difficulty.value,
        request.count,
    )
    return questions


@router.post("/from-resume", response_model=list[QuestionResponse])
async def generate_resume_questions(
    resume_data: ResumeQuestionGenerateCreate,
    user_id: str = Depends(get_current_user),
):
    """Generate interview questions tailored to resume skills."""
    parsed = ResumeParserService.parse_resume(resume_data.resume)
    skills = parsed.get("skills", [])
    questions = LLMService.generate_resume_questions(
        skills,
        resume_data.difficulty.value,
        count=5,
    )
    return questions


@router.get("/next", response_model=QuestionResponse)
async def get_next_question(
    interview_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db),
):
    """Return the next unanswered question for an interview."""
    interview = await db.interviews.find_one({"_id": interview_id})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview["userId"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    answers = interview.get("answers", [])
    questions = interview.get("questions", [])
    next_index = len(answers)
    if next_index >= len(questions):
        raise HTTPException(status_code=404, detail="No next question available")

    return questions[next_index]
