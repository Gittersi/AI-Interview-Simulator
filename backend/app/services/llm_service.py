from typing import List, Optional
from app.config import settings
import logging
import uuid

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with LLM APIs (OpenAI, Anthropic, etc.)"""
    
    @staticmethod
    def generate_questions(category: str, difficulty: str, count: int = 5) -> List[dict]:
        """Generate interview questions using LLM."""
        # In development mode prefer fast deterministic defaults to avoid
        # hitting external LLM APIs (which can be slow or rate-limited).
        if settings.DEBUG:
            return LLMService._get_default_questions(category, difficulty, count)

        try:
            if settings.OPENAI_API_KEY:
                return LLMService._generate_with_openai(category, difficulty, count)
            elif settings.ANTHROPIC_API_KEY:
                return LLMService._generate_with_anthropic(category, difficulty, count)
            else:
                return LLMService._get_default_questions(category, difficulty, count)
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return LLMService._get_default_questions(category, difficulty, count)

    @staticmethod
    def generate_resume_questions(skills: List[str], difficulty: str, count: int = 5) -> List[dict]:
        """Generate interview questions tailored to extracted resume skills."""
        normalized_skills = [skill.strip().lower() for skill in skills if skill.strip()]
        if not normalized_skills:
            return LLMService._get_default_questions("algorithms", difficulty, count)

        # Use default resume-based questions in development to avoid slow LLM calls
        if settings.DEBUG:
            return LLMService._get_resume_default_questions(normalized_skills, difficulty, count)

        try:
            if settings.OPENAI_API_KEY:
                return LLMService._generate_resume_with_openai(normalized_skills, difficulty, count)
            if settings.ANTHROPIC_API_KEY:
                return LLMService._generate_resume_with_anthropic(normalized_skills, difficulty, count)
        except Exception as e:
            logger.error(f"Error generating resume questions: {e}")

        return LLMService._get_resume_default_questions(normalized_skills, difficulty, count)
    
    @staticmethod
    def _generate_with_openai(category: str, difficulty: str, count: int) -> List[dict]:
        """Generate questions using OpenAI API."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            prompt = f"Generate {count} technical interview questions for {category} at {difficulty} level. Return as JSON array with fields: text, category, difficulty, timeLimit."
            
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer. Generate realistic interview questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse response (simplified - real implementation would parse JSON)
            return LLMService._parse_llm_response(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return LLMService._get_default_questions(category, difficulty, count)

    @staticmethod
    def _generate_resume_with_openai(skills: List[str], difficulty: str, count: int) -> List[dict]:
        """Generate resume-specific questions using OpenAI API."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            prompt = (
                f"Generate {count} {difficulty} technical interview questions for a candidate "
                f"with these resume skills: {', '.join(skills)}. Return a JSON array with "
                "fields: text, category, difficulty, timeLimit."
            )

            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer tailoring questions to a resume."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            questions = LLMService._parse_llm_response(response.choices[0].message.content)
            return questions or LLMService._get_resume_default_questions(skills, difficulty, count)
        except Exception as e:
            logger.error(f"OpenAI resume question error: {e}")
            return LLMService._get_resume_default_questions(skills, difficulty, count)
    
    @staticmethod
    def _generate_with_anthropic(category: str, difficulty: str, count: int) -> List[dict]:
        """Generate questions using Anthropic API."""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            
            prompt = f"Generate {count} technical interview questions for {category} at {difficulty} level. Return as JSON array."
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return LLMService._parse_llm_response(response.content[0].text)
        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            return LLMService._get_default_questions(category, difficulty, count)

    @staticmethod
    def _generate_resume_with_anthropic(skills: List[str], difficulty: str, count: int) -> List[dict]:
        """Generate resume-specific questions using Anthropic API."""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

            prompt = (
                f"Generate {count} {difficulty} technical interview questions for these resume skills: "
                f"{', '.join(skills)}. Return a JSON array with fields: text, category, difficulty, timeLimit."
            )

            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            questions = LLMService._parse_llm_response(response.content[0].text)
            return questions or LLMService._get_resume_default_questions(skills, difficulty, count)
        except Exception as e:
            logger.error(f"Anthropic resume question error: {e}")
            return LLMService._get_resume_default_questions(skills, difficulty, count)
    
    @staticmethod
    def _get_default_questions(category: str, difficulty: str, count: int) -> List[dict]:
        """Return default questions when LLM is not available."""
        questions = {
            "data_structures": {
                "easy": [
                    {"text": "Explain what a linked list is and its advantages over arrays.", "timeLimit": 300},
                    {"text": "What is the difference between a stack and a queue?", "timeLimit": 300},
                ],
                "medium": [
                    {"text": "How would you detect a cycle in a linked list?", "timeLimit": 600},
                    {"text": "Explain the concept of balanced binary search trees.", "timeLimit": 600},
                ],
                "hard": [
                    {"text": "Design an algorithm to serialize and deserialize a binary tree.", "timeLimit": 900},
                ]
            },
            "algorithms": {
                "easy": [
                    {"text": "Explain the concept of binary search.", "timeLimit": 300},
                ],
                "medium": [
                    {"text": "What is dynamic programming? Give an example.", "timeLimit": 600},
                ],
                "hard": [
                    {"text": "Design an algorithm to find the longest increasing subsequence.", "timeLimit": 900},
                ]
            }
        }
        
        return LLMService.normalize_questions(
            questions.get(category, {}).get(difficulty, []),
            category,
            difficulty,
        )[:count]

    @staticmethod
    def _get_resume_default_questions(skills: List[str], difficulty: str, count: int) -> List[dict]:
        """Return deterministic resume-based questions when an LLM is not configured."""
        templates = [
            "Walk me through a project where you used {skill}. What tradeoffs did you make?",
            "How would you explain {skill} to a teammate who is new to it?",
            "Describe a debugging challenge you solved while working with {skill}.",
            "What best practices do you follow when using {skill} in production?",
            "How would you improve performance or reliability in a system that uses {skill}?",
        ]
        questions = []

        for index in range(count):
            skill = skills[index % len(skills)]
            questions.append({
                "text": templates[index % len(templates)].format(skill=skill),
                "category": skill,
                "difficulty": difficulty,
                "timeLimit": 600 if difficulty == "medium" else 300 if difficulty == "easy" else 900,
            })

        return LLMService.normalize_questions(questions, "resume", difficulty)

    @staticmethod
    def normalize_questions(questions: List[dict], category: str, difficulty: str) -> List[dict]:
        """Ensure generated questions match the API/frontend question shape."""
        normalized = []
        for question in questions:
            normalized.append({
                "id": question.get("id") or str(uuid.uuid4()),
                "text": question.get("text", ""),
                "category": question.get("category") or category,
                "difficulty": question.get("difficulty") or difficulty,
                "timeLimit": question.get("timeLimit") or 300,
            })
        return normalized
    
    @staticmethod
    def _parse_llm_response(response_text: str) -> List[dict]:
        """Parse LLM response and extract questions."""
        # Simplified parsing - in production, use proper JSON parsing
        try:
            import json
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group())
                return questions
        except:
            pass
        
        return []
    
    @staticmethod
    def generate_feedback(answer: str, question: str) -> str:
        """Generate detailed feedback using LLM."""
        # In development, avoid external LLM calls (slow and may hit quotas)
        if settings.DEBUG or not settings.OPENAI_API_KEY:
            return "Good effort! Review the key concepts and try similar problems to improve."

        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical interviewer providing constructive feedback."
                    },
                    {
                        "role": "user",
                        "content": f"Question: {question}\n\nAnswer: {answer}\n\nProvide specific, actionable feedback."
                    }
                ],
                max_tokens=500
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")

        return "Good effort! Review the key concepts and try similar problems to improve."
