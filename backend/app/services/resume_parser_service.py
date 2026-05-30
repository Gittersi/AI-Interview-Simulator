import spacy
import re
from typing import List, Dict

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = spacy.blank("en")

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
        doc = nlp(resume_text)
        experiences = []
        
        for ent in doc.ents:
            if ent.label_ == "ORG":
                experiences.append(ent.text)
        
        return experiences
    
    @staticmethod
    def extract_education(resume_text: str) -> List[str]:
        """Extract educational background."""
        doc = nlp(resume_text)
        education = []
        
        for ent in doc.ents:
            if ent.label_ in ["ORG", "GPE"]:
                if any(word in resume_text.lower() for word in ["degree", "university", "college", "school"]):
                    education.append(ent.text)
        
        return education
    
    @staticmethod
    def parse_resume(resume_text: str) -> Dict:
        """Complete resume parsing."""
        return {
            "skills": ResumeParserService.extract_skills(resume_text),
            "experience": ResumeParserService.extract_experience(resume_text),
            "education": ResumeParserService.extract_education(resume_text)
        }
