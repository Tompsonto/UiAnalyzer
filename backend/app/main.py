from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.api.analysis import router as analysis_router
from app.core.config import settings

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 ClarityCheck API starting up...")
    
    # Install Playwright browsers on first run
    try:
        os.system("playwright install chromium")
        print("✅ Playwright browsers installed")
    except Exception as e:
        print(f"⚠️  Playwright installation warning: {e}")
    
    yield
    
    # Shutdown
    print("🛑 ClarityCheck API shutting down...")

# Create FastAPI app
app = FastAPI(
    title="ClarityCheck API",
    description="Website Visual Clarity and Text Readability Analysis API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "ClarityCheck API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ClarityCheck API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )