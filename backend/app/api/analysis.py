"""
Analysis API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio
from urllib.parse import urlparse
import logging

from app.core.database import get_db
from app.models.analysis import Analysis
from app.modules.renderer import WebsiteRenderer
from app.modules.visual_analysis import AdvancedVisualAnalyzer
from app.modules.text_analysis import TextAnalyzer
from app.modules.scoring import ScoringEngine

logger = logging.getLogger(__name__)
router = APIRouter()

# Request/Response models
class AnalysisRequest(BaseModel):
    url: HttpUrl
    user_id: Optional[int] = None

class AnalysisResponse(BaseModel):
    id: int
    url: str
    status: str
    overall_score: Optional[float] = None
    visual_score: Optional[float] = None
    text_score: Optional[float] = None
    grade: Optional[str] = None
    issues: Optional[List[dict]] = None
    recommendations: Optional[List[dict]] = None
    created_at: str

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

@router.post("/analyze", response_model=AnalysisResponse)
async def create_analysis(
    request: AnalysisRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new website analysis
    """
    try:
        # Extract domain from URL
        parsed_url = urlparse(str(request.url))
        domain = parsed_url.netloc
        
        # Create initial analysis record
        analysis = Analysis(
            url=str(request.url),
            domain=domain,
            overall_score=0,
            visual_score=0,
            text_score=0,
            grade="F",
            status="pending"
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Start background analysis
        background_tasks.add_task(process_analysis, analysis.id, str(request.url))
        
        return AnalysisResponse(
            id=analysis.id,
            url=analysis.url,
            status=analysis.status,
            created_at=analysis.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error creating analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create analysis: {str(e)}")

@router.post("/analyze/quick", response_model=QuickAnalysisResponse)
async def quick_analysis(request: AnalysisRequest):
    """
    Perform quick analysis without storing in database
    """
    try:
        # Perform analysis
        result = await perform_website_analysis(str(request.url))
        
        return QuickAnalysisResponse(
            overall_score=result['overall_score'],
            visual_score=result['visual_score'],
            text_score=result['text_score'],
            grade=result['grade'],
            summary=result['summary'],
            total_issues=result['total_issues'],
            critical_issues=result['critical_issues'],
            top_issues=result['issues'][:5],  # Top 5 issues
            top_recommendations=result['recommendations'][:3]  # Top 3 recommendations
        )
        
    except Exception as e:
        logger.error(f"Quick analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Get analysis by ID
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return AnalysisResponse(
        id=analysis.id,
        url=analysis.url,
        status=analysis.status,
        overall_score=analysis.overall_score,
        visual_score=analysis.visual_score,
        text_score=analysis.text_score,
        grade=analysis.grade,
        issues=analysis.issues,
        recommendations=analysis.recommendations,
        created_at=analysis.created_at.isoformat()
    )

@router.get("/analyses", response_model=List[AnalysisResponse])
async def get_analyses(
    skip: int = 0, 
    limit: int = 20, 
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of analyses
    """
    query = db.query(Analysis)
    
    if user_id:
        # In a real app, you'd have user_id in the Analysis model
        pass
    
    analyses = query.offset(skip).limit(limit).all()
    
    return [
        AnalysisResponse(
            id=analysis.id,
            url=analysis.url,
            status=analysis.status,
            overall_score=analysis.overall_score,
            visual_score=analysis.visual_score,
            text_score=analysis.text_score,
            grade=analysis.grade,
            issues=analysis.issues,
            recommendations=analysis.recommendations,
            created_at=analysis.created_at.isoformat()
        )
        for analysis in analyses
    ]

@router.delete("/analysis/{analysis_id}")
async def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Delete analysis
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    db.delete(analysis)
    db.commit()
    
    return {"message": "Analysis deleted successfully"}

# Background task functions
async def process_analysis(analysis_id: int, url: str):
    """
    Background task to process website analysis
    """
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    try:
        # Update status to processing
        analysis.status = "processing"
        db.commit()
        
        # Perform analysis
        result = await perform_website_analysis(url)
        
        # Update analysis with results
        analysis.overall_score = result['overall_score']
        analysis.visual_score = result['visual_score']
        analysis.text_score = result['text_score']
        analysis.grade = result['grade']
        analysis.visual_analysis = result.get('score_breakdown', {}).get('visual')
        analysis.text_analysis = result.get('score_breakdown', {}).get('text')
        analysis.issues = result['issues']
        analysis.recommendations = result['recommendations']
        analysis.status = "completed"
        
        db.commit()
        
    except Exception as e:
        # Update analysis with error
        analysis.status = "failed"
        analysis.error_message = str(e)
        db.commit()
        logger.error(f"Analysis {analysis_id} failed: {str(e)}")
    
    finally:
        db.close()

async def perform_website_analysis(url: str) -> dict:
    """
    Perform complete website analysis
    """
    # Initialize analyzers
    visual_analyzer = AdvancedVisualAnalyzer()
    text_analyzer = TextAnalyzer()
    scoring_engine = ScoringEngine()
    
    # Render website and extract data
    async with WebsiteRenderer() as renderer:
        page_data = await renderer.render_website(url)
    
    # Perform visual analysis
    visual_result = visual_analyzer.analyze_visual_clarity(page_data)
    
    # Perform text analysis
    text_result = text_analyzer.analyze_text_readability(page_data)
    
    # Calculate final scores
    final_result = scoring_engine.calculate_overall_score(visual_result, text_result)
    
    return final_result

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check for analysis service
    """
    return {
        "status": "healthy",
        "service": "analysis",
        "capabilities": [
            "website_rendering",
            "visual_analysis", 
            "text_analysis",
            "scoring"
        ]
    }