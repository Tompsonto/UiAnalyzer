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
from app.modules.visual_analysis import analyze_visual
from app.modules.text_analysis import TextAnalyzer
from app.modules.scoring import ScoringEngine
from app.modules.a11y_runner import run_a11y
from app.modules.cta_detector import detect_ctas
from app.modules.multi_viewport_renderer import render_multi_viewport

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
    # Frontend compatibility fields
    visual_issues: Optional[List[dict]] = []
    visual_recommendations: Optional[List[dict]] = []
    text_seo_issues: Optional[List[dict]] = []
    text_seo_recommendations: Optional[List[dict]] = []
    screenshot_url: Optional[str] = None
    url_analyzed: Optional[str] = None

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
            top_recommendations=result['recommendations'][:3],  # Top 3 recommendations
            # Frontend compatibility fields
            visual_issues=result.get('visual_issues', []),
            visual_recommendations=result.get('visual_recommendations', []),
            text_seo_issues=result.get('text_seo_issues', []),
            text_seo_recommendations=result.get('text_seo_recommendations', []),
            screenshot_url=result.get('screenshot_url'),
            url_analyzed=result.get('url_analyzed')
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
    Perform complete website analysis including accessibility, CTA, and multi-viewport
    """
    # Initialize analyzers
    text_analyzer = TextAnalyzer()
    scoring_engine = ScoringEngine()
    
    # Render website and extract data (use multi-viewport renderer)
    multi_viewport_report = await render_multi_viewport(
        url, 
        viewports=['desktop', 'mobile'], 
        timings=['T1'], 
        use_cache=True
    )
    
    # Use desktop T1 data as primary analysis data
    primary_result = next(
        (r for r in multi_viewport_report.results if r.viewport == 'desktop' and r.timing == 'T1'), 
        multi_viewport_report.results[0] if multi_viewport_report.results else None
    )
    
    if not primary_result:
        raise Exception("No rendering results available")
    
    # Prepare data for analyses
    dom = primary_result.dom_content
    css_snapshot = {
        'computed_styles': primary_result.computed_styles,
        'elements': primary_result.element_bounding_boxes
    }
    viewport = (1440, 900)  # Desktop viewport
    
    # Perform visual analysis with existing module
    visual_report = analyze_visual(dom, css_snapshot, viewport)
    
    # Run accessibility analysis
    try:
        a11y_report = await run_a11y(url)
        logger.info(f"Accessibility analysis: {len(a11y_report.issues)} issues found")
    except Exception as e:
        logger.error(f"Accessibility analysis failed: {e}")
        a11y_report = None
    
    # Run CTA analysis
    try:
        cta_report = detect_ctas(
            dom, 
            primary_result.element_bounding_boxes, 
            primary_result.computed_styles,
            viewport_width=1440,
            viewport_height=900
        )
        logger.info(f"CTA analysis: {len(cta_report.ctas)} CTAs found")
    except Exception as e:
        logger.error(f"CTA analysis failed: {e}")
        cta_report = None
    
    # Debug logging
    logger.info(f"Visual analysis completed: score={visual_report.score}, issues={len(visual_report.issues)}")
    logger.info(f"Element data provided: {len(css_snapshot.get('elements', []))} elements")
    
    # Convert to frontend-compatible format
    visual_result = {
        'visual_score': visual_report.score,
        'score_breakdown': visual_report.features,
        'issues': [
            {
                'type': issue.type,
                'selector': issue.selector,
                'bbox': issue.bbox,
                'severity': issue.severity,
                'message': issue.message,
                'element': issue.selector,  # Frontend expects 'element' field
                'suggestion': _get_visual_suggestion(issue.type, issue.severity)  # Proper suggestion
            }
            for issue in visual_report.issues
        ],
        'recommendations': _generate_recommendations_from_issues(visual_report.issues),
        # Frontend compatibility fields
        'visual_issues': [
            {
                'element': issue.selector,
                'severity': issue.severity,
                'message': issue.message,
                'suggestion': _get_visual_suggestion(issue.type, issue.severity),
                'type': issue.type
            }
            for issue in visual_report.issues
        ],
        'visual_recommendations': _generate_recommendations_from_issues(visual_report.issues)
    }
    
    # Add accessibility results
    if a11y_report:
        visual_result['accessibility_score'] = max(0, 100 - (len(a11y_report.issues) * 10))
        visual_result['accessibility_issues'] = [
            {
                'element': issue.selector,
                'severity': _map_a11y_severity(issue.impact),
                'message': issue.message,
                'suggestion': f'Fix {issue.internal_type} issue: {issue.rule_id}',
                'type': issue.internal_type
            }
            for issue in a11y_report.issues
        ]
    else:
        visual_result['accessibility_score'] = 0
        visual_result['accessibility_issues'] = []
    
    # Add CTA analysis results
    if cta_report:
        visual_result['cta_score'] = round(sum(cta.overall_score for cta in cta_report.ctas) / max(len(cta_report.ctas), 1))
        visual_result['cta_analysis'] = {
            'total_ctas': cta_report.total_ctas_found,
            'above_fold_ctas': cta_report.above_fold_ctas,
            'primary_cta': {
                'text': cta_report.primary_cta.text,
                'score': cta_report.primary_cta.overall_score,
                'above_fold': cta_report.primary_cta.above_fold
            } if cta_report.primary_cta else None,
            'cta_issues': [
                {
                    'element': cta.selector,
                    'text': cta.text,
                    'severity': 'high' if cta.overall_score < 50 else 'medium' if cta.overall_score < 75 else 'low',
                    'message': f'CTA "{cta.text}" has issues affecting usability',
                    'suggestion': f'Improve CTA score from {cta.overall_score:.0f}/100',
                    'score': cta.overall_score,
                    'above_fold': cta.above_fold,
                    'is_primary': cta.is_primary
                }
                for cta in cta_report.ctas if cta.overall_score < 80
            ]
        }
    else:
        visual_result['cta_score'] = 0
        visual_result['cta_analysis'] = {'total_ctas': 0, 'above_fold_ctas': 0, 'primary_cta': None, 'cta_issues': []}
    
    # Add multi-viewport data
    visual_result['multi_viewport'] = {
        'total_processing_time': multi_viewport_report.total_processing_time,
        'cache_hit': multi_viewport_report.cache_hit,
        'viewports_analyzed': len(multi_viewport_report.results),
        'mobile_data': None,
        'desktop_data': None
    }
    
    # Add viewport-specific data
    for result in multi_viewport_report.results:
        viewport_data = {
            'viewport': result.viewport,
            'timing': result.timing,
            'screenshot_base64': result.screenshot_base64,
            'elements_detected': len(result.element_bounding_boxes),
            'render_metrics': result.render_metrics
        }
        
        if result.viewport == 'mobile':
            visual_result['multi_viewport']['mobile_data'] = viewport_data
        elif result.viewport == 'desktop':
            visual_result['multi_viewport']['desktop_data'] = viewport_data
    
    # Debug the visual result
    logger.info(f"Visual result issues: {len(visual_result['issues'])}")
    
    # Prepare page data for text analysis (convert to old format)
    page_data = {
        'text_content': dom,
        'html_content': dom,
        'dom_analysis': {
            'headings': [elem for elem in primary_result.element_bounding_boxes if elem.get('text') and any(h in elem.get('selector', '') for h in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
        }
    }
    
    # Perform text analysis
    text_result = text_analyzer.analyze_text_readability(page_data)
    
    # Calculate final scores
    final_result = scoring_engine.calculate_overall_score(visual_result, text_result)
    
    # Add screenshots from multi-viewport results
    if primary_result and primary_result.screenshot_base64:
        final_result['screenshot_url'] = f"data:image/png;base64,{primary_result.screenshot_base64}"
    
    # Ensure visual and text issues are in the expected format
    final_result['visual_issues'] = visual_result.get('visual_issues', [])
    final_result['visual_recommendations'] = visual_result.get('visual_recommendations', [])
    # Process text issues to ensure proper structure
    text_issues = text_result.get('issues', [])
    final_result['text_seo_issues'] = [
        {
            'element': issue.get('element', 'Content'),
            'severity': issue.get('severity', 'medium'),
            'message': issue.get('message', ''),
            'suggestion': issue.get('suggestion', ''),
            'type': issue.get('type', 'readability')
        }
        for issue in text_issues
    ]
    final_result['text_seo_recommendations'] = text_result.get('recommendations', [])
    final_result['url_analyzed'] = url
    
    # Add new analysis results to final result
    final_result['accessibility_score'] = visual_result.get('accessibility_score', 0)
    final_result['accessibility_issues'] = visual_result.get('accessibility_issues', [])
    final_result['cta_score'] = visual_result.get('cta_score', 0)
    final_result['cta_analysis'] = visual_result.get('cta_analysis', {})
    final_result['multi_viewport'] = visual_result.get('multi_viewport', {})
    
    # Add to overall scoring (adjust weights)
    if final_result.get('accessibility_score', 0) > 0 or final_result.get('cta_score', 0) > 0:
        # Recalculate overall score including new metrics
        base_score = final_result.get('overall_score', 0)
        accessibility_score = final_result.get('accessibility_score', 0)
        cta_score = final_result.get('cta_score', 0)
        
        # Weighted average with existing score
        enhanced_score = (
            base_score * 0.7 +
            accessibility_score * 0.15 +
            cta_score * 0.15
        )
        
        final_result['overall_score'] = round(enhanced_score, 1)
        final_result['enhanced_analysis'] = True
    
    return final_result

def _map_a11y_severity(impact: str) -> str:
    """Map axe-core impact levels to our severity levels"""
    mapping = {
        'critical': 'high',
        'serious': 'high', 
        'moderate': 'medium',
        'minor': 'low'
    }
    return mapping.get(impact, 'medium')

def _get_visual_suggestion(issue_type: str, severity: str) -> str:
    """Generate specific suggestions based on issue type and severity"""
    suggestions = {
        'contrast': {
            'high': 'Use darker text colors or lighter background colors to meet WCAG AA standards',
            'medium': 'Increase color contrast between text and background',
            'low': 'Consider slightly darkening text or lightening background for better accessibility'
        },
        'typography': {
            'high': 'Increase font size to at least 16px for desktop or 14px for mobile',
            'medium': 'Increase line-height to at least 1.3 times the font size',
            'low': 'Limit line length to 45-75 characters by reducing text width'
        },
        'tap_target': {
            'high': 'Increase button/link size to at least 44x44px with adequate spacing',
            'medium': 'Make touch targets larger for easier mobile interaction',
            'low': 'Add more padding around interactive elements'
        },
        'overlap': {
            'high': 'Adjust positioning, margins, or z-index to prevent element overlap',
            'medium': 'Fix overlapping elements that may hide content',
            'low': 'Review layout to ensure proper element spacing'
        },
        'density': {
            'high': 'Distribute elements across more space or use progressive disclosure',
            'medium': 'Reduce number of interactive elements in this area',
            'low': 'Group related elements and add more whitespace'
        },
        'alignment': {
            'high': 'Align elements to a consistent grid using CSS flexbox or grid',
            'medium': 'Fix alignment issues to improve visual consistency',
            'low': 'Ensure elements align to a common baseline'
        }
    }
    
    return suggestions.get(issue_type, {}).get(severity, 'Review and fix this issue for better user experience')

def _get_text_suggestion(issue_type: str, severity: str) -> str:
    """Generate specific suggestions for text analysis issues"""
    suggestions = {
        'readability': {
            'high': 'Simplify language, use shorter sentences, and replace complex words',
            'medium': 'Simplify some complex sentences where possible',
            'low': 'Consider using simpler vocabulary in some sections'
        },
        'structure': {
            'high': 'Add proper heading structure with a clear H1 tag',
            'medium': 'Fix heading hierarchy and break up long paragraphs', 
            'low': 'Improve content organization and structure'
        },
        'complexity': {
            'high': 'Keep sentences under 20 words and use active voice',
            'medium': 'Reduce sentence length and use more active voice',
            'low': 'Replace some complex words with simpler alternatives'
        }
    }
    
    return suggestions.get(issue_type, {}).get(severity, 'Improve content clarity and readability')

def _generate_recommendations_from_issues(issues) -> List[dict]:
    """
    Generate recommendations from visual analysis issues
    """
    recommendations = []
    issue_types = [issue.type for issue in issues]
    
    # Contrast recommendations
    if 'contrast' in issue_types:
        contrast_issues = [issue for issue in issues if issue.type == 'contrast']
        high_contrast_issues = [issue for issue in contrast_issues if issue.severity == 'high']
        
        recommendations.append({
            'category': 'WCAG Compliance',
            'priority': 'Critical' if high_contrast_issues else 'High',
            'action': 'Fix Color Contrast Issues',
            'description': f'Resolve {len(contrast_issues)} contrast issues to meet WCAG AA standards',
            'impact': 'Accessibility, Legal Compliance',
            'effort': 'Medium'
        })
    
    # Typography recommendations
    if 'typography' in issue_types:
        typography_issues = [issue for issue in issues if issue.type == 'typography']
        recommendations.append({
            'category': 'Typography',
            'priority': 'High',
            'action': 'Improve Font Sizes and Spacing',
            'description': f'Fix {len(typography_issues)} typography issues for better readability',
            'impact': 'User Experience, Accessibility',
            'effort': 'Low'
        })
    
    # Tap target recommendations
    if 'tap_target' in issue_types:
        tap_issues = [issue for issue in issues if issue.type == 'tap_target']
        recommendations.append({
            'category': 'Mobile Usability',
            'priority': 'High',
            'action': 'Increase Touch Target Sizes',
            'description': f'Make {len(tap_issues)} interactive elements easier to tap on mobile',
            'impact': 'Mobile Experience, Usability',
            'effort': 'Medium'
        })
    
    # Overlap recommendations
    if 'overlap' in issue_types:
        overlap_issues = [issue for issue in issues if issue.type == 'overlap']
        recommendations.append({
            'category': 'Layout',
            'priority': 'Medium',
            'action': 'Fix Overlapping Elements',
            'description': f'Resolve {len(overlap_issues)} overlapping UI components',
            'impact': 'Visual Clarity, User Experience',
            'effort': 'Medium'
        })
    
    # Density recommendations
    if 'density' in issue_types:
        density_issues = [issue for issue in issues if issue.type == 'density']
        recommendations.append({
            'category': 'UI Design',
            'priority': 'Medium',
            'action': 'Reduce Visual Clutter',
            'description': f'Simplify {len(density_issues)} high-density regions',
            'impact': 'Cognitive Load, Focus',
            'effort': 'High'
        })
    
    # Alignment recommendations
    if 'alignment' in issue_types:
        alignment_issues = [issue for issue in issues if issue.type == 'alignment']
        recommendations.append({
            'category': 'Visual Polish',
            'priority': 'Low',
            'action': 'Improve Element Alignment',
            'description': f'Align {len(alignment_issues)} misaligned elements',
            'impact': 'Professional Appearance',
            'effort': 'Low'
        })
    
    return recommendations

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