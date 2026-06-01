from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.database import connect_to_mongo, disconnect_from_mongo
from app.api import auth, interviews, evaluation, users, speech, questions
import logging
from app.services.llm_worker import start_llm_worker, stop_llm_worker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event handlers
@app.on_event("startup")
async def startup():
    await connect_to_mongo()
    # Start background LLM worker (will be a no-op if event loop unavailable)
    start_llm_worker()
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown():
    # Stop background worker before disconnecting from DB
    stop_llm_worker()
    await disconnect_from_mongo()
    logger.info("Application shutdown complete")

# Include routers
app.include_router(auth.router)
app.include_router(interviews.router)
app.include_router(evaluation.router)
app.include_router(users.router)
app.include_router(speech.router)
app.include_router(questions.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG
    )
