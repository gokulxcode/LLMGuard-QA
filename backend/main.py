import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core import security
from app.models import models
from app.api import auth, prompts, evaluations, bug_reports, dashboard, reports

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llmguard_qa")

# Initialize database tables
logger.info("Initializing database tables...")
Base.metadata.create_all(bind=engine)

# Seed default admin user if not present
db = SessionLocal()
try:
    admin_user = db.query(models.User).filter(models.User.username == settings.ADMIN_USERNAME).first()
    if not admin_user:
        logger.info(f"Seeding default admin user: {settings.ADMIN_USERNAME}")
        hashed_pwd = security.get_password_hash(settings.ADMIN_PASSWORD)
        default_admin = models.User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password_hash=hashed_pwd,
            role="admin"
        )
        db.add(default_admin)
        db.commit()
except Exception as e:
    logger.error(f"Error seeding default administrator: {e}")
finally:
    db.close()

# Create FastAPI App
app = FastAPI(
    title="LLMGuard QA API",
    description="AI-Powered Testing Framework for Generative AI Applications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth.router, prefix="/api")
app.include_router(prompts.router, prefix="/api")
app.include_router(evaluations.router, prefix="/api")
app.include_router(bug_reports.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app_name": "LLMGuard QA API",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
