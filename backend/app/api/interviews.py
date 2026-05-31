from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.schemas import InterviewCreate, InterviewResponse, AnswerCreate, ResumeInterviewCreate
from app.services.auth_service import AuthService
from app.services.llm_service import LLMService
from app.services.llm_worker import enqueue_task
from app.config import settings
from app.services.evaluation_service import EvaluationService
from app.services.resume_parser_service import ResumeParserService
from app.db.database import get_db
from bson import ObjectId
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/interviews", tags=["interviews"])
security = HTTPBearer()

def build_interview_response(interview: dict) -> InterviewResponse:
    questions = interview.get("questions", [])
    return InterviewResponse(
        id=interview["_id"],
        userId=interview["userId"],
        startTime=interview["startTime"],
        endTime=interview.get("endTime"),
        status=interview["status"],
        questionCount=len(questions),
        category=interview.get("category"),
        difficulty=interview.get("difficulty"),
        questions=questions
    )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
    user_id = AuthService.decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return user_id

@router.post("", response_model=InterviewResponse)
async def start_interview(
    interview_data: InterviewCreate,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Start a new interview."""
    interview_id = str(uuid.uuid4())
    # Immediately return fast deterministic/default questions to keep latency low.
    fast_questions = LLMService._get_default_questions(
        interview_data.category,
        interview_data.difficulty,
        count=5
    )
    questions = LLMService.normalize_questions(
        fast_questions,
        interview_data.category,
        interview_data.difficulty
    )
    # If real LLMs are configured and mock mode is not enabled, enqueue background task
    llm_enabled = (
        not settings.DEBUG
        and not settings.LLM_USE_MOCK
        and (settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY)
    )
    
    interview = {
        "_id": interview_id,
        "userId": user_id,
        "startTime": datetime.utcnow(),
        "endTime": None,
        "status": "in_progress",
        "category": interview_data.category,
        "difficulty": interview_data.difficulty,
        "questions": questions,
        "llm_status": "pending" if llm_enabled else "done",
        "answers": []
    }
    
    await db.interviews.insert_one(interview)

    if llm_enabled:
        enqueue_task({
            "type": "generate_questions",
            "interview_id": interview_id,
            "category": interview_data.category,
            "difficulty": interview_data.difficulty,
            "count": 5,
        })
    
    return build_interview_response(interview)

@router.post("/from-resume", response_model=InterviewResponse)
async def start_resume_interview(
    resume_data: ResumeInterviewCreate,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Start a new interview from pasted resume text."""
    parsed = ResumeParserService.parse_resume(resume_data.resumeText)
    skills = parsed.get("skills", [])
    # Provide immediate resume-based default questions and enqueue LLM generation if enabled
    fast_questions = LLMService._get_resume_default_questions(skills, resume_data.difficulty, count=5)
    questions = LLMService.normalize_questions(fast_questions, "resume", resume_data.difficulty)
    llm_enabled = (
        not settings.DEBUG
        and not settings.LLM_USE_MOCK
        and (settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY)
    )

    interview_id = str(uuid.uuid4())
    interview = {
        "_id": interview_id,
        "userId": user_id,
        "startTime": datetime.utcnow(),
        "endTime": None,
        "status": "in_progress",
        "category": "resume",
        "difficulty": resume_data.difficulty,
        "resumeData": parsed,
        "questions": questions,
        "llm_status": "pending" if llm_enabled else "done",
        "answers": []
    }

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "resume": resume_data.resumeText,
                "resumeData": parsed,
                "skills": skills,
            }
        }
    )
    await db.interviews.insert_one(interview)

    if llm_enabled:
        enqueue_task({
            "type": "generate_questions",
            "interview_id": interview_id,
            "category": "resume",
            "difficulty": resume_data.difficulty,
            "count": 5,
            "skills": skills,
        })

    return build_interview_response(interview)

@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get interview details."""
    interview = await db.interviews.find_one({"_id": interview_id})
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if interview["userId"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    return build_interview_response(interview)

@router.post("/{interview_id}/submit")
async def submit_answer(
    interview_id: str,
    answer_data: AnswerCreate,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Submit an answer for a question."""
    interview = await db.interviews.find_one({"_id": interview_id})
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if interview["userId"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Determine question text for evaluation
    question_text = None
    try:
        for q in interview.get("questions", []):
            if q.get("id") == answer_data.questionId:
                question_text = q.get("text")
                break
    except Exception:
        question_text = None

    if question_text is None:
        # Fallback: try by index
        try:
            q_index = len(interview.get("answers", []))
            question_text = interview.get("questions", [])[q_index].get("text")
        except Exception:
            question_text = ""

    # Evaluate answer server-side and include LLM feedback
    evaluation = EvaluationService.evaluate_answer(answer_data.text, question_text)
    feedback = LLMService.generate_feedback(answer_data.text, question_text)
    evaluation["llm_feedback"] = feedback

    # Store answer with evaluation
    answer = {
        "questionId": answer_data.questionId,
        "questionIndex": len(interview.get("answers", [])),
        "text": answer_data.text,
        "audioUrl": answer_data.audioUrl,
        "code": answer_data.code,
        "evaluation": evaluation,
        "timestamp": datetime.utcnow()
    }

    await db.interviews.update_one(
        {"_id": interview_id},
        {"$push": {"answers": answer}}
    )

    return {"status": "success", "answerId": str(uuid.uuid4()), "evaluation": evaluation}

@router.post("/{interview_id}/complete")
async def complete_interview(
    interview_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Mark interview as completed."""
    interview = await db.interviews.find_one({"_id": interview_id})
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if interview["userId"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    await db.interviews.update_one(
        {"_id": interview_id},
        {"$set": {"status": "completed", "endTime": datetime.utcnow()}}
    )
    
    return {"status": "success"}

@router.get("")
async def get_interview_history(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get user's interview history."""
    interviews = await db.interviews.find({"userId": user_id}).to_list(100)
    
    return [
        {
            "id": i["_id"],
            "startTime": i["startTime"],
            "status": i["status"],
            "category": i.get("category", ""),
            "difficulty": i.get("difficulty", "")
        }
        for i in interviews
    ]
