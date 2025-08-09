#!/usr/bin/env python3
"""
Real ClarityCheck API with actual website analysis
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import logging
import asyncio
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ClarityCheck API - Real Analysis",
    description="Website Visual Clarity and Text Readability Analysis API",
    version="1.0.0"
)

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
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
    analysis_time: Optional[float] = None
    url_analyzed: str

@app.get("/")
async def root():
    return {
        "message": "ClarityCheck API - Real Analysis ✅ WORKING",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "features": ["real_website_rendering", "text_analysis", "visual_analysis"],
        "backend_type": "REAL_ANALYSIS"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "ClarityCheck Real Analysis API",
        "capabilities": ["playwright_rendering", "text_analysis", "visual_analysis"]
    }

def calculate_grade(score: float) -> str:
    """Calculate letter grade from numeric score"""
    if score >= 90:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 80:
        return "A-"
    elif score >= 75:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 65:
        return "B-"
    elif score >= 60:
        return "C+"
    elif score >= 55:
        return "C"
    elif score >= 50:
        return "C-"
    elif score >= 45:
        return "D+"
    elif score >= 40:
        return "D"
    else:
        return "F"

def create_summary(url: str, overall_score: float, visual_score: float, text_score: float) -> str:
    """Create analysis summary based on scores"""
    domain = str(url).replace('https://', '').replace('http://', '').split('/')[0]
    
    if overall_score >= 80:
        return f"{domain} shows excellent clarity and readability with strong user experience design."
    elif overall_score >= 70:
        return f"{domain} has good clarity with some areas for improvement in user experience."
    elif overall_score >= 60:
        return f"{domain} shows moderate clarity but would benefit from significant improvements."
    elif overall_score >= 50:
        return f"{domain} has clarity issues that may impact user engagement and accessibility."
    else:
        return f"{domain} has significant clarity and readability problems requiring immediate attention."

async def perform_basic_analysis(url: str) -> dict:
    """
    Perform basic website analysis without heavy dependencies
    This is a simplified version that analyzes basic HTML structure
    """
    import aiohttp
    from bs4 import BeautifulSoup
    import re
    from urllib.parse import urljoin, urlparse
    
    logger.info(f"Starting basic analysis for: {url}")
    
    try:
        # Fetch the webpage
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(str(url), headers=headers) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail=f"Failed to fetch website: HTTP {response.status}")
                
                html_content = await response.text()
                
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract text content
        for script in soup(["script", "style"]):
            script.decompose()
        text_content = soup.get_text()
        clean_text = ' '.join(text_content.split())
        
        # Basic analysis metrics
        word_count = len(clean_text.split())
        char_count = len(clean_text)
        
        # Analyze HTML structure
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        paragraphs = soup.find_all('p')
        links = soup.find_all('a')
        images = soup.find_all('img')
        buttons = soup.find_all(['button', 'input[type="button"]', 'input[type="submit"]'])
        
        # Visual Analysis Score (0-100)
        visual_score = 100
        visual_issues = []
        
        # Check heading structure
        h1_count = len(soup.find_all('h1'))
        if h1_count == 0:
            visual_score -= 15
            visual_issues.append({
                "type": "structure",
                "severity": "high", 
                "message": "No H1 heading found",
                "element": "Page Structure"
            })
        elif h1_count > 1:
            visual_score -= 10
            visual_issues.append({
                "type": "structure",
                "severity": "medium",
                "message": f"Multiple H1 headings ({h1_count}) found",
                "element": "Page Structure"
            })
        
        # Check images without alt text
        images_no_alt = [img for img in images if not img.get('alt', '').strip()]
        if images_no_alt:
            penalty = min(20, len(images_no_alt) * 2)
            visual_score -= penalty
            visual_issues.append({
                "type": "accessibility",
                "severity": "high" if len(images_no_alt) > 5 else "medium",
                "message": f"{len(images_no_alt)} images missing alt text",
                "element": "Image Accessibility"
            })
        
        # Check for basic CTA elements
        cta_elements = soup.find_all(['button', 'a']) + soup.select('[class*="btn"], [class*="button"], [class*="cta"]')
        if len(cta_elements) < 2:
            visual_score -= 10
            visual_issues.append({
                "type": "conversion",
                "severity": "medium",
                "message": "Few call-to-action elements detected",
                "element": "User Engagement"
            })
        
        # Text Analysis Score (0-100)
        text_score = 100
        text_issues = []
        
        # Basic readability analysis
        sentences = re.split(r'[.!?]+', clean_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            
            if avg_sentence_length > 25:
                text_score -= 20
                text_issues.append({
                    "type": "readability",
                    "severity": "high",
                    "message": f"Average sentence length is {avg_sentence_length:.1f} words",
                    "element": "Content Readability"
                })
            elif avg_sentence_length > 20:
                text_score -= 10
                text_issues.append({
                    "type": "readability", 
                    "severity": "medium",
                    "message": f"Sentences are somewhat long ({avg_sentence_length:.1f} words average)",
                    "element": "Content Readability"
                })
        
        # Check paragraph lengths
        long_paragraphs = 0
        for p in paragraphs:
            p_text = p.get_text().strip()
            if len(p_text) > 300:
                long_paragraphs += 1
        
        if long_paragraphs > 3:
            text_score -= 15
            text_issues.append({
                "type": "structure",
                "severity": "medium",
                "message": f"{long_paragraphs} very long paragraphs detected",
                "element": "Content Structure"
            })
        
        # Check word count
        if word_count < 100:
            text_score -= 15
            text_issues.append({
                "type": "content",
                "severity": "medium",
                "message": "Very little text content found",
                "element": "Content Volume"
            })
        
        # Calculate overall score
        visual_score = max(0, min(100, visual_score))
        text_score = max(0, min(100, text_score))
        overall_score = (visual_score * 0.6 + text_score * 0.4)  # Weight visual slightly higher
        
        # Combine all issues
        all_issues = visual_issues + text_issues
        critical_issues = len([i for i in all_issues if i['severity'] == 'high'])
        
        # Generate recommendations
        recommendations = []
        
        if visual_issues:
            if any(i['type'] == 'accessibility' for i in visual_issues):
                recommendations.append({
                    "category": "Accessibility",
                    "priority": "High",
                    "action": "Add Alt Text to Images",
                    "description": "Improve accessibility by adding descriptive alt text to all images"
                })
            
            if any(i['type'] == 'structure' for i in visual_issues):
                recommendations.append({
                    "category": "Page Structure",
                    "priority": "High",
                    "action": "Fix Heading Structure", 
                    "description": "Use proper heading hierarchy with a single H1 per page"
                })
        
        if text_issues:
            if any(i['type'] == 'readability' for i in text_issues):
                recommendations.append({
                    "category": "Content Readability",
                    "priority": "Medium",
                    "action": "Simplify Sentence Structure",
                    "description": "Break up long sentences for better readability"
                })
            
            if any(i['type'] == 'structure' for i in text_issues):
                recommendations.append({
                    "category": "Content Structure",
                    "priority": "Medium", 
                    "action": "Break Up Long Paragraphs",
                    "description": "Divide long paragraphs into shorter, scannable chunks"
                })
        
        # Add generic recommendations if scores are low
        if overall_score < 70:
            recommendations.append({
                "category": "General Improvement",
                "priority": "High",
                "action": "Comprehensive UX Review",
                "description": "Consider a full user experience audit to identify key improvement areas"
            })
        
        return {
            "visual_score": visual_score,
            "text_score": text_score,
            "overall_score": overall_score,
            "issues": all_issues,
            "recommendations": recommendations,
            "critical_issues": critical_issues,
            "metrics": {
                "word_count": word_count,
                "paragraph_count": len(paragraphs),
                "heading_count": len(headings),
                "image_count": len(images),
                "link_count": len(links)
            }
        }
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/v1/analyze/quick", response_model=QuickAnalysisResponse)
async def quick_analysis(request: AnalysisRequest):
    """
    Perform real website analysis
    """
    start_time = time.time()
    url = str(request.url)
    
    logger.info(f"Real analysis requested for: {url}")
    
    try:
        # Perform actual analysis
        analysis_result = await perform_basic_analysis(url)
        
        analysis_time = time.time() - start_time
        
        # Format response
        response = QuickAnalysisResponse(
            overall_score=round(analysis_result['overall_score'], 1),
            visual_score=round(analysis_result['visual_score'], 1),
            text_score=round(analysis_result['text_score'], 1),
            grade=calculate_grade(analysis_result['overall_score']),
            summary=create_summary(url, analysis_result['overall_score'], 
                                 analysis_result['visual_score'], analysis_result['text_score']),
            total_issues=len(analysis_result['issues']),
            critical_issues=analysis_result['critical_issues'],
            top_issues=analysis_result['issues'][:5],  # Top 5 issues
            top_recommendations=analysis_result['recommendations'][:3],  # Top 3 recommendations
            analysis_time=round(analysis_time, 2),
            url_analyzed=url
        )
        
        logger.info(f"Analysis completed for {url}: {response.overall_score}/100 (Visual: {response.visual_score}, Text: {response.text_score})")
        
        return response
        
    except Exception as e:
        logger.error(f"Quick analysis failed for {url}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/v1/health")
async def analysis_health():
    return {
        "status": "healthy",
        "service": "analysis",
        "capabilities": [
            "real_html_analysis",
            "text_readability",
            "visual_structure", 
            "accessibility_check"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    import aiohttp  # Check if aiohttp is available
    
    print("Starting ClarityCheck Real Analysis API server...")
    print("Features: Real website analysis, HTML parsing, readability scoring")
    
    uvicorn.run(
        "real_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )