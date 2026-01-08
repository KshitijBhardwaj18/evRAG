"""
Main FastAPI application for EvRAG
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .core.logging import log
from .api.routes import datasets, evaluations
from .db.session import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    log.info("Starting EvRAG API server")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    log.info("Database initialized")
    yield
    
    log.info("Shutting down EvRAG API server")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade RAG Evaluation Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(datasets.router, prefix="/api")
app.include_router(evaluations.router, prefix="/api")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "name": settings.APP_NAME,
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENV == "development"
    )

