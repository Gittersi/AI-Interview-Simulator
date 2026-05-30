try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    SPACY_AVAILABLE = False

import re
from typing import List, Dict, Optional
from app.config import settings
import logging
import json

logger = logging.getLogger(__name__)

if SPACY_AVAILABLE:
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        nlp = None
else:
    nlp = None

class ResumeParserService:
    """Service for parsing and extracting information from resumes."""
    
    SKILL_KEYWORDS = {
        'programming': ['python', 'java', 'javascript', 'c++', 'csharp', 'ruby', 'php', 'golang', 'rust', 'kotlin'],
        'web': ['html', 'css', 'react', 'vue', 'angular', 'nodejs', 'fastapi', 'django', 'flask', 'express'],
        'database': ['sql', 'mongodb', 'postgres', 'mysql', 'redis', 'elasticsearch', 'dynamodb'],
        'tools': ['git', 'docker', 'kubernetes', 'jenkins', 'aws', 'gcp', 'azure', 'linux'],
        'soft_skills': ['leadership', 'communication', 'teamwork', 'problem-solving', 'analytical']
    }
    
    @staticmethod
    def extract_skills(resume_text: str) -> List[str]:
        """Extract skills from resume text."""
        resume_lower = resume_text.lower()
        found_skills = []
        
        for category, skills in ResumeParserService.SKILL_KEYWORDS.items():
            for skill in skills:
                if skill in resume_lower:
                    found_skills.append(skill)
        
        return list(set(found_skills))
    
    @staticmethod
    def extract_experience(resume_text: str) -> List[str]:
        """Extract professional experiences from resume."""
        experiences = []
        if nlp:
            doc = nlp(resume_text)
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    experiences.append(ent.text)
        else:
            for line in resume_text.splitlines():
                if any(term in line.lower() for term in ["at ", "with ", "for ", "as a "]):
                    if len(line.strip()) > 20:
                        experiences.append(line.strip())
        return list(dict.fromkeys(experiences))
    
    @staticmethod
    def extract_education(resume_text: str) -> List[str]:
        """Extract educational background."""
        education = []
        text_lower = resume_text.lower()
        if nlp:
            doc = nlp(resume_text)
            for ent in doc.ents:
                if ent.label_ in ["ORG", "GPE"]:
                    if any(word in text_lower for word in ["degree", "university", "college", "school"]):
                        education.append(ent.text)
        else:
            if any(word in text_lower for word in ["degree", "university", "college", "school"]):
                matches = re.findall(r"(degree|university|college|school)[^\n\.\,]*", resume_text, flags=re.IGNORECASE)
                for match in matches:
                    education.append(match.strip())
        return list(dict.fromkeys([item for item in education if item]))
    
    @staticmethod
    def parse_resume(resume_text: str) -> Dict:
        """Complete resume parsing."""
        return {
            "skills": ResumeParserService.extract_skills(resume_text),
            "experience": ResumeParserService.extract_experience(resume_text),
            "education": ResumeParserService.extract_education(resume_text)
        }
    
    @staticmethod
    def extract_keywords_from_job_description(job_description: str) -> List[str]:
        """Extract relevant skill keywords from a job description."""
        found = set()
        jd = job_description.lower()
        for skills in ResumeParserService.SKILL_KEYWORDS.values():
            for keyword in skills:
                if keyword in jd:
                    found.add(keyword)
        return sorted(found)
    
    @staticmethod
    def calculate_missing_keywords(resume_text: str, job_description: Optional[str] = None) -> List[str]:
        """Determine which job description keywords are missing from the resume."""
        if not job_description:
            return []
        resume_skills = set(ResumeParserService.extract_skills(resume_text))
        job_keywords = set(ResumeParserService.extract_keywords_from_job_description(job_description))
        missing = sorted([kw for kw in job_keywords if kw not in resume_skills])
        return missing
    
    @staticmethod
    def _calculate_job_match_score(skills: List[str], job_description: Optional[str] = None) -> Optional[int]:
        """Compute a simple job match score based on required keywords."""
        if not job_description:
            return None
        job_keywords = ResumeParserService.extract_keywords_from_job_description(job_description)
        if not job_keywords:
            return None
        matched = len([kw for kw in job_keywords if kw in skills])
        score = int((matched / len(job_keywords)) * 100)
        return min(100, max(0, score))
    
    @staticmethod
    def calculate_ats_score(resume_text: str, job_description: Optional[str] = None) -> Dict:
        """
        Calculate ATS (Applicant Tracking System) score using LLM analysis.
        Returns score and detailed feedback.
        """
        try:
            if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
                logger.warning("No LLM API key configured for ATS scoring")
                return ResumeParserService._calculate_basic_ats_score(resume_text)
            
            logger.info("Starting LLM-based ATS analysis")
            
            if settings.OPENAI_API_KEY:
                return ResumeParserService._analyze_resume_with_openai(resume_text, job_description)
            elif settings.ANTHROPIC_API_KEY:
                return ResumeParserService._analyze_resume_with_anthropic(resume_text, job_description)
            else:
                return ResumeParserService._calculate_basic_ats_score(resume_text)
                
        except Exception as e:
            logger.error(f"ATS analysis error: {e}")
            return ResumeParserService._calculate_basic_ats_score(resume_text, job_description)
    
    @staticmethod
    def _analyze_resume_with_openai(resume_text: str, job_description: Optional[str] = None) -> Dict:
        """Analyze resume using OpenAI GPT."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Prepare the prompt
            job_context = f"\n\nJob Description:\n{job_description}" if job_description else ""
            
            prompt = f"""Analyze this resume for ATS (Applicant Tracking System) compatibility and quality. Provide a detailed JSON response.

Resume:
{resume_text}
{job_context}

Provide a JSON response with the following structure:
{{
    "ats_score": <0-100>,
    "ats_grade": "<A/B/C/D/F>",
    "formatting_score": <0-100>,
    "keyword_score": <0-100>,
    "content_quality_score": <0-100>,
    "summary": "<brief summary of overall quality>",
    "strengths": ["<strength1>", "<strength2>", ...],
    "weaknesses": ["<weakness1>", "<weakness2>", ...],
    "improvements": [
        {{"category": "<formatting/keywords/structure/content>", "suggestion": "<specific improvement>"}}
    ],
    "keywords_found": ["<keyword1>", "<keyword2>", ...],
    "keywords_missing": ["<recommended keyword>", ...],
    "formatting_issues": ["<issue1>", "<issue2>"],
    "job_match_score": <0-100 if job description provided, null otherwise>
}}

Focus on:
1. ATS parsing compatibility (proper sections, clear formatting)
2. Keyword optimization for job matching
3. Content quality and clarity
4. Professional presentation
5. Length and structure appropriate for the role"""

            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert ATS analyst and resume coach. Provide detailed, actionable feedback in valid JSON format."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                logger.info(f"ATS analysis complete: score={result.get('ats_score', 'N/A')}")
                return result
            else:
                logger.warning("Could not parse ATS analysis response")
                return ResumeParserService._calculate_basic_ats_score(resume_text)
                
        except Exception as e:
            logger.error(f"OpenAI ATS analysis error: {e}")
            return ResumeParserService._calculate_basic_ats_score(resume_text)
    
    @staticmethod
    def _analyze_resume_with_anthropic(resume_text: str, job_description: Optional[str] = None) -> Dict:
        """Analyze resume using Anthropic Claude."""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            
            job_context = f"\n\nJob Description:\n{job_description}" if job_description else ""
            
            prompt = f"""Analyze this resume for ATS (Applicant Tracking System) compatibility and quality. Provide a detailed JSON response.

Resume:
{resume_text}
{job_context}

Provide a JSON response with the following structure:
{{
    "ats_score": <0-100>,
    "ats_grade": "<A/B/C/D/F>",
    "formatting_score": <0-100>,
    "keyword_score": <0-100>,
    "content_quality_score": <0-100>,
    "summary": "<brief summary of overall quality>",
    "strengths": ["<strength1>", "<strength2>", ...],
    "weaknesses": ["<weakness1>", "<weakness2>", ...],
    "improvements": [
        {{"category": "<formatting/keywords/structure/content>", "suggestion": "<specific improvement>"}}
    ],
    "keywords_found": ["<keyword1>", "<keyword2>", ...],
    "keywords_missing": ["<recommended keyword>", ...],
    "formatting_issues": ["<issue1>", "<issue2>"],
    "job_match_score": <0-100 if job description provided, null otherwise>
}}"""

            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                logger.info(f"ATS analysis complete: score={result.get('ats_score', 'N/A')}")
                return result
            else:
                logger.warning("Could not parse ATS analysis response")
                return ResumeParserService._calculate_basic_ats_score(resume_text)
                
        except Exception as e:
            logger.error(f"Anthropic ATS analysis error: {e}")
            return ResumeParserService._calculate_basic_ats_score(resume_text)
    
    @staticmethod
    def _calculate_basic_ats_score(resume_text: str, job_description: Optional[str] = None) -> Dict:
        """
        Calculate basic ATS score without LLM (fallback).
        Evaluates formatting, keywords, and structure.
        """
        score_components = {}
        
        # Formatting score (0-30 points)
        formatting_score = 0
        if len(resume_text) < 500:
            formatting_score = 10  # Too short
        elif len(resume_text) > 3000:
            formatting_score = 20  # Reasonable but lengthy
        else:
            formatting_score = 30  # Good length
        
        # Check for structure
        has_sections = any(keyword in resume_text.lower() for keyword in [
            'experience', 'education', 'skills', 'summary', 'objective'
        ])
        if has_sections:
            formatting_score += 10
        
        score_components['formatting_score'] = min(100, formatting_score)
        
        # Keyword score (0-35 points)
        parsed = ResumeParserService.parse_resume(resume_text)
        skills_found = len(parsed.get('skills', []))
        keyword_score = min(35, skills_found * 5)
        score_components['keyword_score'] = keyword_score
        
        # Content quality (0-35 points)
        content_score = 20
        if parsed.get('experience'):
            content_score += 10
        if parsed.get('education'):
            content_score += 5
        score_components['content_quality_score'] = min(100, content_score)
        
        # Calculate overall ATS score
        ats_score = (
            score_components['formatting_score'] * 0.3 +
            score_components['keyword_score'] * 0.4 +
            score_components['content_quality_score'] * 0.3
        )
        
        ats_score = min(100, int(ats_score))
        
        # Determine grade
        if ats_score >= 90:
            grade = 'A'
        elif ats_score >= 80:
            grade = 'B'
        elif ats_score >= 70:
            grade = 'C'
        elif ats_score >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            "ats_score": ats_score,
            "ats_grade": grade,
            "formatting_score": score_components['formatting_score'],
            "keyword_score": score_components['keyword_score'],
            "content_quality_score": score_components['content_quality_score'],
            "summary": f"Your resume has an ATS score of {ats_score} ({grade}). Focus on adding more industry keywords and improving structure.",
            "strengths": [
                "Resume has proper sections" if has_sections else "Resume is readable",
                f"Found {skills_found} key skills" if skills_found > 0 else "Limited skills mentioned"
            ],
            "weaknesses": [
                "Add more specific technical keywords" if skills_found < 5 else "",
                "Improve professional formatting" if formatting_score < 60 else ""
            ],
            "improvements": [
                {"category": "keywords", "suggestion": "Add industry-specific technical skills to increase keyword score"},
                {"category": "structure", "suggestion": "Use clear section headers (Experience, Education, Skills, etc.)"},
                {"category": "formatting", "suggestion": "Use simple formatting, avoid tables and graphics for ATS compatibility"}
            ],
            "keywords_found": parsed.get('skills', []),
            "keywords_missing": ResumeParserService.calculate_missing_keywords(resume_text, job_description),
            "formatting_issues": [
                "Consider simpler formatting for better ATS parsing"
            ],
            "job_match_score": ResumeParserService._calculate_job_match_score(parsed.get('skills', []), job_description)
        }

    @staticmethod
    def rewrite_resume_for_job(resume_text: str, job_description: str) -> Dict:
        """Rewrite the resume to align with the provided job description."""
        try:
            if settings.OPENAI_API_KEY:
                return ResumeParserService._rewrite_resume_with_openai(resume_text, job_description)
            if settings.ANTHROPIC_API_KEY:
                return ResumeParserService._rewrite_resume_with_anthropic(resume_text, job_description)
        except Exception as e:
            logger.error(f"Resume rewrite LLM error: {e}")

        return ResumeParserService._rewrite_resume_fallback(resume_text, job_description)

    @staticmethod
    def _rewrite_resume_with_openai(resume_text: str, job_description: str) -> Dict:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            prompt = f"""Rewrite this resume so it is better-tailored for the following job description. Preserve the candidate's experience and achievements while optimizing for ATS keyword matching, section structure, and a professional tone.

Resume:
{resume_text}

Job Description:
{job_description}

Return a JSON object with keys: updated_resume, summary, suggestions, keywords_added, keywords_missing, job_match_score."""

            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert resume coach and ATS writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            response_text = response.choices[0].message.content
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            logger.warning("Could not parse resume rewrite response from OpenAI")
        except Exception as e:
            logger.error(f"OpenAI resume rewrite error: {e}")

        return ResumeParserService._rewrite_resume_fallback(resume_text, job_description)

    @staticmethod
    def _rewrite_resume_with_anthropic(resume_text: str, job_description: str) -> Dict:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            prompt = f"""Rewrite this resume so it is better-tailored for the following job description. Preserve the candidate's experience and achievements while optimizing for ATS keyword matching, section structure, and a professional tone.

Resume:
{resume_text}

Job Description:
{job_description}

Return a JSON object with keys: updated_resume, summary, suggestions, keywords_added, keywords_missing, job_match_score."""

            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            logger.warning("Could not parse resume rewrite response from Anthropic")
        except Exception as e:
            logger.error(f"Anthropic resume rewrite error: {e}")

        return ResumeParserService._rewrite_resume_fallback(resume_text, job_description)

    @staticmethod
    def _rewrite_resume_fallback(resume_text: str, job_description: str) -> Dict:
        missing_keywords = ResumeParserService.calculate_missing_keywords(resume_text, job_description)
        job_keywords = ResumeParserService.extract_keywords_from_job_description(job_description)
        updated_resume = resume_text
        summary = (
            "No LLM key is configured, so the resume cannot be rewritten automatically. "
            "Use the keyword guidance below to update your resume for this job description."
        )
        suggestions = [
            "Add missing keywords from the job description into your skills and experience sections.",
            "Use simple ATS-friendly formatting with clear headers like Experience, Education, and Skills.",
            "Keep achievements concise and focused on results and technical contributions."
        ]

        return {
            "updated_resume": updated_resume,
            "summary": summary,
            "suggestions": suggestions,
            "keywords_added": missing_keywords,
            "keywords_missing": missing_keywords,
            "job_match_score": ResumeParserService._calculate_job_match_score(ResumeParserService.extract_skills(resume_text), job_description),
            "job_keywords": job_keywords
        }
