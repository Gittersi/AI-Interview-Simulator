import asyncio
import logging
from typing import Any, Dict, Optional

from app.config import settings
from app.services.llm_service import LLMService
from app.db.database import get_db

logger = logging.getLogger(__name__)

# Simple in-process background queue for LLM tasks. This is lightweight scaffolding
# intended for local development. For production, replace with a durable worker
# (Celery/RQ) and a persistent queue (Redis/RabbitMQ).
queue: asyncio.Queue = asyncio.Queue()
_worker_task: Optional[asyncio.Task] = None


async def _worker_loop() -> None:
    logger.info("LLM worker loop starting")
    db = get_db()

    while True:
        task: Dict[str, Any] = await queue.get()
        try:
            ttype = task.get("type")
            if ttype == "generate_questions":
                interview_id = task["interview_id"]
                category = task.get("category", "algorithms")
                difficulty = task.get("difficulty", "easy")
                count = int(task.get("count", 5))
                skills = task.get("skills")

                logger.info("LLM worker processing interview=%s type=generate_questions", interview_id)

                if skills:
                    questions = LLMService.generate_resume_questions(skills, difficulty, count)
                    normalized = LLMService.normalize_questions(questions, "resume", difficulty)
                else:
                    questions = LLMService.generate_questions(category, difficulty, count)
                    normalized = LLMService.normalize_questions(questions, category, difficulty)

                try:
                    await db.interviews.update_one(
                        {"_id": interview_id},
                        {"$set": {"questions": normalized, "llm_status": "done"}}
                    )
                    logger.info("LLM worker updated interview %s with %d questions", interview_id, len(normalized))
                except Exception as e:
                    logger.error("Failed to update interview %s: %s", interview_id, e)
                    try:
                        await db.interviews.update_one(
                            {"_id": interview_id},
                            {"$set": {"llm_status": "failed", "llm_error": str(e)}}
                        )
                    except Exception:
                        logger.exception("Also failed to persist llm failure for interview %s", interview_id)
            else:
                logger.warning("LLM worker received unknown task type: %s", ttype)
        except Exception as e:
            logger.exception("Unhandled error in LLM worker: %s", e)
        finally:
            try:
                queue.task_done()
            except Exception:
                pass


def enqueue_task(task: Dict[str, Any]) -> None:
    try:
        queue.put_nowait(task)
        logger.info("Enqueued LLM task: %s", task.get("type"))
    except Exception as e:
        logger.error("Failed to enqueue LLM task: %s", e)


def start_llm_worker() -> None:
    """Start the background worker task on the running event loop."""
    global _worker_task
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop (shouldn't happen during FastAPI startup)
        logger.warning("No running event loop; LLM worker not started")
        return

    if _worker_task is None or _worker_task.done():
        _worker_task = loop.create_task(_worker_loop())
        logger.info("LLM worker task created")


def stop_llm_worker() -> None:
    global _worker_task
    if _worker_task:
        _worker_task.cancel()
        _worker_task = None
        logger.info("LLM worker task cancelled")
