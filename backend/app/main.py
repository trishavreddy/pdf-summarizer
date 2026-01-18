from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import create_db_and_tables
from app.routers.auth import router as auth_router, users_router
from app.routers.pdf import router as pdf_router
from app.routers.summary import router as summary_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    await create_db_and_tables()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="PDF Summarizer API",
    description="API for uploading PDFs and generating AI-powered summaries",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(pdf_router)
app.include_router(summary_router)


@app.get("/")
async def root():
    return {
        "message": "PDF Summarizer API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
