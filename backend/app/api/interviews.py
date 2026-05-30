from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.schemas import InterviewCreate, InterviewResponse, AnswerCreate, ResumeInterviewCreate
from app.services.auth_service import AuthService
from app.services.llm_service import LLMService
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
    
    # Generate questions
    questions = LLMService.generate_questions(
        category=interview_data.category,
        difficulty=interview_data.difficulty,
        count=5
    )
    questions = LLMService.normalize_questions(
        questions,
        interview_data.category,
        interview_data.difficulty
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
        "answers": []
    }
    
    await db.interviews.insert_one(interview)
    
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
    questions = LLMService.generate_resume_questions(
        skills=skills,
        difficulty=resume_data.difficulty,
        count=5
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
    
    # Store answer
    answer = {
        "questionId": answer_data.questionId,
        "questionIndex": len(interview.get("answers", [])),
        "text": answer_data.text,
        "audioUrl": answer_data.audioUrl,
        "code": answer_data.code,
        "timestamp": datetime.utcnow()
    }
    
    await db.interviews.update_one(
        {"_id": interview_id},
        {"$push": {"answers": answer}}
    )
    
    return {"status": "success", "answerId": str(uuid.uuid4())}

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
