import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.models.job import Job
from app.auth.security import hash_password
from app.ingestion.pipeline import JobIngestionPipeline
from app.resume.extractor import CandidateExtractor
from app.embeddings.embedder import embedding_service

from app.api.auth import router as auth_router
from app.api.jobs import router as jobs_router
from app.api.resume import router as resume_router
from app.api.search import router as search_router
from app.api.agent import router as agent_router
from app.api.tracker import router as tracker_router
from app.api.skill_gap import router as skill_gap_router
from app.api.evaluation import router as evaluation_router

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("careermatch")

def initialize_database_data():
    """Seeds the initial database schema, demo candidate profile, and job opportunities."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Create default demo user if not exists
        demo_user = db.query(User).filter(User.email == "demo@careermatch.ai").first()
        if not demo_user:
            logger.info("Seeding demo user...")
            demo_user = User(
                email="demo@careermatch.ai",
                hashed_password=hash_password("DemoPassword123!"),
                full_name="Alex Chen",
                is_active=True,
                is_admin=True,
                preferences_json=json.dumps({
                    "target_titles": ["AI Engineer", "Backend Software Engineer", "ML Engineer"],
                    "preferred_locations": ["Remote", "San Francisco, CA"],
                    "remote_only": False,
                    "min_salary": 120000,
                    "target_skills": ["python", "pytorch", "fastapi", "rag", "docker"]
                })
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)

            # Seed default candidate resume profile for demo user
            sample_resume = (
                "Alex Chen\nalex.chen@example.com | San Francisco, CA | (555) 123-4567\n\n"
                "SUMMARY\n"
                "Software Engineer with 3+ years experience building scalable backend APIs, machine learning pipelines, "
                "and retrieval systems. Proven track record deploying FastAPI microservices, fine-tuning PyTorch models, "
                "and designing hybrid search with vector embeddings.\n\n"
                "WORK EXPERIENCE\n"
                "Software Engineer — AI Infrastructure\n"
                "Nexus Tech (2023 - Present)\n"
                "- Built high-throughput RAG search service using FastAPI, pgvector, and PyTorch, reducing latency by 45%.\n"
                "- Implemented Docker containerization and CI/CD pipelines deployed on AWS ECS.\n"
                "- Designed relational data models in PostgreSQL with SQLAlchemy and Redis caching.\n\n"
                "Junior Backend Developer\n"
                "CloudFlow Systems (2021 - 2023)\n"
                "- Developed RESTful APIs in Python and Node.js for data ingestion pipelines.\n"
                "- Wrote unit and integration test suites achieving 88% code coverage.\n\n"
                "EDUCATION\n"
                "B.S. in Computer Science\n"
                "University of California, Berkeley (2017 - 2021)\n\n"
                "PROJECTS\n"
                "Semantic Document Retriever\n"
                "- Built hybrid BM25 and vector search engine using sentence-transformers and FastAPI.\n\n"
                "SKILLS\n"
                "Languages: Python, TypeScript, SQL\n"
                "AI/ML: PyTorch, NLP, RAG, Machine Learning, Transformers\n"
                "Backend & Cloud: FastAPI, Docker, AWS, PostgreSQL, Redis, REST API\n"
                "Frontend: React, Tailwind CSS\n"
            )

            structured_prof = CandidateExtractor.extract_profile(sample_resume)
            skills_str = ", ".join([s.name for s in structured_prof.skills])
            embed_text = f"Alex Chen. mid engineer. Skills: {skills_str}. Summary: {structured_prof.summary}."
            vector_embed = embedding_service.embed_text(embed_text)

            profile = CandidateProfile(
                user_id=demo_user.id,
                raw_resume_text=sample_resume,
                resume_filename="alex_chen_resume.pdf",
                structured_data_json=structured_prof.model_dump_json(),
                embedding_json=json.dumps(vector_embed)
            )
            db.add(profile)
            db.commit()

        # 2. Ingest Jobs if database is empty
        job_count = db.query(Job).count()
        if job_count == 0:
            logger.info("Job database empty. Running initial job ingestion pipeline...")
            pipeline = JobIngestionPipeline(db)
            stats = pipeline.run()
            logger.info(f"Initial job ingestion complete: {stats}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing CareerMatch AI Backend...")
    initialize_database_data()
    yield
    # Shutdown
    logger.info("CareerMatch AI Backend shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent AI-powered career agent, semantic job retrieval, and multi-signal ranking platform.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again."}
    )

# Health checks
@app.get("/health")
@app.get(f"{settings.API_V1_PREFIX}/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "1.0.0"
    }

# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(jobs_router, prefix=settings.API_V1_PREFIX)
app.include_router(resume_router, prefix=settings.API_V1_PREFIX)
app.include_router(search_router, prefix=settings.API_V1_PREFIX)
app.include_router(agent_router, prefix=settings.API_V1_PREFIX)
app.include_router(tracker_router, prefix=settings.API_V1_PREFIX)
app.include_router(skill_gap_router, prefix=settings.API_V1_PREFIX)
app.include_router(evaluation_router, prefix=settings.API_V1_PREFIX)
