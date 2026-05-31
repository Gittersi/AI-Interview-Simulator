from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.schemas import ResumeTextCreate, ResumeUpdateCreate, UserResponse
from app.services.auth_service import AuthService
from app.services.resume_parser_service import ResumeParserService
from app.db.database import get_db
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/users", tags=["users"])
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

@router.get("/profile", response_model=UserResponse)
async def get_profile(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get user profile."""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user["name"],
        skills=user.get("skills", [])
    )

@router.put("/profile")
async def update_profile(
    profile_data: dict,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Update user profile."""
    update_data = {
        "name": profile_data.get("name"),
        "skills": profile_data.get("skills", [])
    }
    
    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    return {"status": "success"}

@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Upload and parse resume."""
    try:
        content = await file.read()
        resume_text = content.decode('utf-8')
        
        # Parse resume
        parsed = ResumeParserService.parse_resume(resume_text)
        
        # Store in database
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "resume": resume_text,
                    "resumeData": parsed
                }
            }
        )
        
        return {
            "status": "success",
            "skills": parsed.get("skills", []),
            "experience": parsed.get("experience", []),
            "education": parsed.get("education", [])
        }
    except Exception as e:
        logger.error(f"Resume upload error: {e}")
        raise HTTPException(status_code=400, detail="Failed to parse resume")

@router.post("/resume/text")
async def parse_resume_text(
    resume_data: ResumeTextCreate,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Parse pasted resume text and save extracted resume data."""
    try:
        parsed = ResumeParserService.parse_resume(resume_data.resumeText)

        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "resume": resume_data.resumeText,
                    "resumeData": parsed,
                    "skills": parsed.get("skills", []),
                }
            }
        )

        return {
            "status": "success",
            "skills": parsed.get("skills", []),
            "experience": parsed.get("experience", []),
            "education": parsed.get("education", []),
        }
    except Exception as e:
        logger.error(f"Resume text parse error: {e}")
        raise HTTPException(status_code=400, detail="Failed to parse resume")

@router.get("/progress")
async def get_progress(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get user's progress metrics."""
    interviews = await db.interviews.find({"userId": user_id}).to_list(100)
    
    total_interviews = len(interviews)
    completed_interviews = len([i for i in interviews if i["status"] == "completed"])
    
    # Calculate average scores
    reports = await db.reports.find({"userId": user_id}).to_list(100)
    
    if reports:
        avg_score = sum(r.get("totalScore", 0) for r in reports) / len(reports)
    else:
        avg_score = 0
    
    return {
        "totalInterviews": total_interviews,
        "completedInterviews": completed_interviews,
        "averageScore": avg_score,
        "improvementTrend": "positive"  # Placeholder
    }


@router.post("/resume/analyze-ats")
async def analyze_resume_ats(
    data: dict,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Analyze resume for ATS (Applicant Tracking System) score."""
    try:
        resume_text = data.get("resumeText")
        job_description = data.get("jobDescription")
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="Resume text is required")
        
        if len(resume_text.strip()) < 100:
            raise HTTPException(status_code=400, detail="Resume text is too short (minimum 100 characters)")
        
        logger.info(f"Analyzing resume for user {user_id}")
        
        # Calculate ATS score using LLM
        ats_analysis = ResumeParserService.calculate_ats_score(resume_text, job_description)
        
        # Store analysis in database
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "resume": resume_text,
                    "atsScore": ats_analysis.get("ats_score"),
                    "atsAnalysis": ats_analysis,
                    "lastAtsAnalysis": __import__('datetime').datetime.utcnow()
                }
            }
        )
        
        logger.info(f"ATS analysis complete: score={ats_analysis.get('ats_score')}")
        
        return {
            "status": "success",
            "analysis": ats_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ATS analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze resume")

@router.post("/resume/update")
async def update_resume_for_job(
    data: ResumeUpdateCreate,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Generate an updated resume tailored to the provided job description."""
    try:
        if not data.resumeText.strip():
            raise HTTPException(status_code=400, detail="Resume text is required")
        if not data.jobDescription.strip():
            raise HTTPException(status_code=400, detail="Job description is required")

        logger.info(f"Updating resume for user {user_id}")
        updated = ResumeParserService.rewrite_resume_for_job(data.resumeText, data.jobDescription)

        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "resume": updated.get("updated_resume", data.resumeText),
                    "resumeData": ResumeParserService.parse_resume(updated.get("updated_resume", data.resumeText)),
                    "resumeUpdate": updated,
                    "lastResumeUpdate": __import__('datetime').datetime.utcnow()
                }
            }
        )

        return {
            "status": "success",
            "updatedResume": updated.get("updated_resume", data.resumeText),
            "analysis": updated
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume update error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update resume")
