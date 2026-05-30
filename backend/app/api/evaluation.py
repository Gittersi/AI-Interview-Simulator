from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.services.auth_service import AuthService
from app.services.evaluation_service import EvaluationService
from app.services.llm_service import LLMService
from app.db.database import get_db
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])
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

@router.post("/answer")
async def evaluate_answer(
    answer_data: dict,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Evaluate a user's answer."""
    answer_text = answer_data.get("answer", "")
    question_text = answer_data.get("question", "")
    
    if not answer_text or not question_text:
        raise HTTPException(status_code=400, detail="Missing answer or question")
    
    # Evaluate answer
    evaluation = EvaluationService.evaluate_answer(answer_text, question_text)
    
    # Get LLM feedback
    feedback = await LLMService.generate_feedback(answer_text, question_text)
    evaluation["llm_feedback"] = feedback
    
    return evaluation

@router.post("/code")
async def evaluate_code(
    code_data: dict,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Evaluate code submission."""
    code = code_data.get("code", "")
    language = code_data.get("language", "python")
    
    if not code:
        raise HTTPException(status_code=400, detail="No code provided")
    
    # Evaluate code
    evaluation = EvaluationService.evaluate_code(code, language)
    
    return evaluation

@router.get("/report/{interview_id}")
async def get_performance_report(
    interview_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get performance report for completed interview."""
    interview = await db.interviews.find_one({"_id": interview_id})
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if interview["userId"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    if interview["status"] != "completed":
        raise HTTPException(status_code=400, detail="Interview not completed")
    
    # Retrieve stored evaluation data
    report = await db.reports.find_one({"interviewId": interview_id})
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not generated yet")
    
    return {
        "interviewId": interview_id,
        "totalScore": report.get("totalScore", 0),
        "correctnessScore": report.get("correctnessScore", 0),
        "communicationScore": report.get("communicationScore", 0),
        "confidenceScore": report.get("confidenceScore", 0),
        "evaluations": report.get("evaluations", []),
        "suggestions": report.get("suggestions", []),
        "timestamp": report.get("timestamp")
    }
