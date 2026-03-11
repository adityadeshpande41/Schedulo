"""
Schedulo FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import schedule, meetings, preferences, agents, calendar
from core.config import settings
from database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Schedulo API starting up...")
    yield
    # Shutdown
    print("👋 Schedulo API shutting down...")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Schedulo API starting up...")
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization skipped: {e}")
    yield
    # Shutdown
    print("👋 Schedulo API shutting down...")


app = FastAPI(
    title="Schedulo API",
    description="AI-powered multi-agent meeting scheduler",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(schedule.router, prefix="/api/schedule", tags=["Schedule"])
app.include_router(meetings.router, prefix="/api/meetings", tags=["Meetings"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["Preferences"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(calendar.router, prefix="/api", tags=["Calendar"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Schedulo API",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agents": {
            "calendar": "operational",
            "behavior": "operational",
            "coordination": "operational",
            "orchestrator": "operational"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
