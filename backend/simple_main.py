#!/usr/bin/env python3
"""
Simple ClarityCheck API for testing frontend connection
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ClarityCheck API",
    description="Website Visual Clarity and Text Readability Analysis API",
    version="1.0.0"
)

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class AnalysisRequest(BaseModel):
    url: HttpUrl

class QuickAnalysisResponse(BaseModel):
    overall_score: float
    visual_score: float
    text_score: float
    grade: str
    summary: str
    total_issues: int
    critical_issues: int
    top_issues: List[dict]
    top_recommendations: List[dict]

@app.get("/")
async def root():
    return {
        "message": "ClarityCheck API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ClarityCheck API"}

@app.post("/api/v1/analyze/quick", response_model=QuickAnalysisResponse)
async def quick_analysis(request: AnalysisRequest):
    """
    Mock quick analysis endpoint for testing frontend
    """
    logger.info(f"Quick analysis requested for: {request.url}")
    
    # Mock analysis result
    return QuickAnalysisResponse(
        overall_score=78.5,
        visual_score=82.0,
        text_score=75.0,
        grade="B+",
        summary=f"Website {request.url} shows good clarity with room for improvement in text readability.",
        total_issues=4,
        critical_issues=1,
        top_issues=[
            {
                "type": "contrast",
                "severity": "high",
                "message": "Low contrast detected in header buttons",
                "element": "CTA Button"
            },
            {
                "type": "typography",
                "severity": "medium", 
                "message": "Font size below 14px in navigation",
                "element": "Navigation Links"
            },
            {
                "type": "readability",
                "severity": "medium",
                "message": "Average sentence length is 22 words",
                "element": "Main Content"
            }
        ],
        top_recommendations=[
            {
                "category": "Visual Design",
                "priority": "High",
                "action": "Improve Color Contrast",
                "description": "Increase contrast ratio for buttons to meet WCAG AA standards"
            },
            {
                "category": "Typography",
                "priority": "Medium", 
                "action": "Increase Font Sizes",
                "description": "Make navigation text at least 14px for better readability"
            },
            {
                "category": "Content",
                "priority": "Medium",
                "action": "Simplify Sentences",
                "description": "Break up long sentences for better comprehension"
            }
        ]
    )

@app.get("/api/v1/health")
async def analysis_health():
    return {
        "status": "healthy",
        "service": "analysis",
        "capabilities": [
            "mock_analysis",
            "frontend_testing"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting ClarityCheck API server...")
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )