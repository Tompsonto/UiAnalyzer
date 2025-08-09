#!/usr/bin/env python3
"""
Simplified Real ClarityCheck API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List
import logging
import time
import re
import aiohttp
import base64
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="ClarityCheck Real Analysis API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    url: HttpUrl

class QuickAnalysisResponse(BaseModel):
    overall_score: float
    visual_score: float
    text_score: float
    clarity_score: float
    grade: str
    summary: str
    screenshot_url: str
    total_issues: int
    critical_issues: int
    conversion_risks: int
    ux_patterns: List[dict]
    visual_issues: List[dict]
    visual_recommendations: List[dict]
    text_seo_issues: List[dict]
    text_seo_recommendations: List[dict]
    analysis_time: float
    url_analyzed: str

@app.get("/")
async def root():
    return {"message": "ClarityCheck REAL Analysis API ✓ WORKING", "version": "2.0.0"}

def analyze_heading_structure(soup):
    """Analyze heading structure and hierarchy"""
    heading_issues = []
    heading_recommendations = []
    
    # Find all heading tags
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    if not headings:
        heading_issues.append({
            "type": "structure",
            "severity": "high",
            "message": "No heading tags found on page",
            "element": "Page Structure",
            "suggestion": "Add heading structure (H1, H2, H3) for better SEO and accessibility"
        })
        return heading_issues, heading_recommendations, 0
    
    # Extract heading levels and text
    heading_structure = []
    for heading in headings:
        level = int(heading.name[1])  # Extract number from h1, h2, etc.
        text = heading.get_text().strip()
        heading_structure.append({
            'level': level,
            'text': text,
            'tag': heading.name.upper()
        })
    
    # Check H1 presence
    h1_headings = [h for h in heading_structure if h['level'] == 1]
    h1_count = len(h1_headings)
    
    score = 100
    
    if h1_count == 0:
        score -= 25
        heading_issues.append({
            "type": "seo",
            "severity": "high",
            "message": "No H1 heading found",
            "element": "H1 Tag",
            "suggestion": "Add exactly one H1 tag as the main page heading"
        })
        heading_recommendations.append({
            "category": "SEO",
            "priority": "Critical",
            "action": "Add H1 Heading",
            "description": "Every page needs exactly one H1 tag for SEO and accessibility"
        })
    elif h1_count > 1:
        score -= 15
        heading_issues.append({
            "type": "seo",
            "severity": "medium",
            "message": f"Multiple H1 headings found ({h1_count})",
            "element": "H1 Tags",
            "suggestion": "Use only one H1 per page, convert others to H2 or H3"
        })
        heading_recommendations.append({
            "category": "SEO",
            "priority": "High",
            "action": "Fix H1 Structure",
            "description": "Use only one H1 heading per page for optimal SEO"
        })
    
    # Check heading hierarchy (proper nesting)
    hierarchy_issues = check_heading_hierarchy(heading_structure)
    if hierarchy_issues:
        score -= 10
        heading_issues.append({
            "type": "structure",
            "severity": "medium",
            "message": "Improper heading hierarchy detected",
            "element": "Heading Hierarchy",
            "suggestion": "Follow logical order: H1 > H2 > H3, don't skip levels",
            "details": hierarchy_issues
        })
        heading_recommendations.append({
            "category": "Structure",
            "priority": "Medium",
            "action": "Fix Heading Hierarchy", 
            "description": "Organize headings in logical order without skipping levels"
        })
    
    # Check for empty headings
    empty_headings = [h for h in heading_structure if not h['text'] or len(h['text']) < 3]
    if empty_headings:
        score -= 8
        heading_issues.append({
            "type": "content",
            "severity": "medium",
            "message": f"{len(empty_headings)} empty or very short headings",
            "element": "Heading Content",
            "suggestion": "Add descriptive text to all headings"
        })
    
    # Check for repeated heading text
    heading_texts = [h['text'].lower() for h in heading_structure if h['text']]
    duplicate_texts = set([text for text in heading_texts if heading_texts.count(text) > 1])
    if duplicate_texts:
        score -= 5
        heading_issues.append({
            "type": "content",
            "severity": "low",
            "message": f"Duplicate heading text found: {', '.join(list(duplicate_texts)[:3])}",
            "element": "Heading Uniqueness",
            "suggestion": "Make heading text unique and descriptive"
        })
    
    return heading_issues, heading_recommendations, max(0, score)

def check_heading_hierarchy(heading_structure):
    """Check if headings follow proper hierarchy"""
    issues = []
    
    if not heading_structure:
        return issues
    
    # Should start with H1
    if heading_structure[0]['level'] != 1:
        issues.append(f"Page should start with H1, but starts with {heading_structure[0]['tag']}")
    
    # Check for level jumping
    for i in range(1, len(heading_structure)):
        current_level = heading_structure[i]['level']
        previous_level = heading_structure[i-1]['level']
        
        # If we jump more than 1 level up (e.g., H1 to H3), that's bad
        if current_level > previous_level + 1:
            issues.append(f"Skipped heading level: {heading_structure[i-1]['tag']} followed by {heading_structure[i]['tag']}")
    
    return issues

def analyze_meta_tags(soup):
    """Analyze meta tags for SEO and social sharing"""
    meta_issues = []
    meta_recommendations = []
    
    score = 100
    
    # Check title tag
    title_tag = soup.find('title')
    if not title_tag or not title_tag.get_text().strip():
        score -= 20
        meta_issues.append({
            "type": "seo",
            "severity": "high", 
            "message": "Missing or empty title tag",
            "element": "Title Tag",
            "suggestion": "Add descriptive title tag (50-60 characters)"
        })
        meta_recommendations.append({
            "category": "SEO",
            "priority": "Critical",
            "action": "Add Title Tag",
            "description": "Every page needs a unique, descriptive title tag"
        })
    else:
        title_length = len(title_tag.get_text().strip())
        if title_length > 60:
            score -= 5
            meta_issues.append({
                "type": "seo",
                "severity": "low",
                "message": f"Title tag too long ({title_length} chars)",
                "element": "Title Length",
                "suggestion": "Keep title under 60 characters for better SERP display"
            })
        elif title_length < 30:
            score -= 3
            meta_issues.append({
                "type": "seo",
                "severity": "low", 
                "message": f"Title tag may be too short ({title_length} chars)",
                "element": "Title Length",
                "suggestion": "Consider a more descriptive title (30-60 characters)"
            })
    
    # Check meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if not meta_desc or not meta_desc.get('content', '').strip():
        score -= 15
        meta_issues.append({
            "type": "seo",
            "severity": "high",
            "message": "Missing meta description",
            "element": "Meta Description",
            "suggestion": "Add meta description (150-160 characters)"
        })
        meta_recommendations.append({
            "category": "SEO",
            "priority": "High",
            "action": "Add Meta Description",
            "description": "Meta descriptions improve click-through rates from search results"
        })
    else:
        desc_length = len(meta_desc.get('content', '').strip())
        if desc_length > 160:
            score -= 5
            meta_issues.append({
                "type": "seo",
                "severity": "low",
                "message": f"Meta description too long ({desc_length} chars)",
                "element": "Meta Description Length",
                "suggestion": "Keep meta description under 160 characters"
            })
        elif desc_length < 120:
            score -= 3
            meta_issues.append({
                "type": "seo",
                "severity": "low",
                "message": f"Meta description may be too short ({desc_length} chars)", 
                "element": "Meta Description Length",
                "suggestion": "Consider a more detailed description (120-160 characters)"
            })
    
    # Check viewport meta tag
    viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
    if not viewport_meta:
        score -= 10
        meta_issues.append({
            "type": "mobile",
            "severity": "medium",
            "message": "Missing viewport meta tag",
            "element": "Viewport Meta",
            "suggestion": "Add viewport meta tag for mobile responsiveness"
        })
        meta_recommendations.append({
            "category": "Mobile",
            "priority": "Medium", 
            "action": "Add Viewport Meta Tag",
            "description": "Essential for mobile-responsive design"
        })
    
    # Check charset
    charset_meta = soup.find('meta', attrs={'charset': True}) or soup.find('meta', attrs={'http-equiv': 'Content-Type'})
    if not charset_meta:
        score -= 5
        meta_issues.append({
            "type": "technical",
            "severity": "low",
            "message": "Missing charset declaration",
            "element": "Charset Meta",
            "suggestion": "Add charset meta tag (usually UTF-8)"
        })
    
    # Check Open Graph tags (social sharing)
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    og_description = soup.find('meta', attrs={'property': 'og:description'})
    og_image = soup.find('meta', attrs={'property': 'og:image'})
    
    og_missing = []
    if not og_title: og_missing.append('og:title')
    if not og_description: og_missing.append('og:description') 
    if not og_image: og_missing.append('og:image')
    
    if og_missing:
        score -= 8
        meta_issues.append({
            "type": "social",
            "severity": "low",
            "message": f"Missing Open Graph tags: {', '.join(og_missing)}",
            "element": "Social Sharing",
            "suggestion": "Add Open Graph tags for better social media sharing"
        })
    
    return meta_issues, meta_recommendations, max(0, score)

def analyze_cta_elements(soup):
    """Analyze call-to-action elements for visibility and effectiveness"""
    cta_issues = []
    cta_data = {}
    
    # Find potential CTAs
    cta_selectors = [
        'button',
        'a[class*="btn"]', 'a[class*="button"]', 'a[class*="cta"]',
        '[class*="btn"]', '[class*="button"]', '[class*="cta"]',
        'input[type="submit"]', 'input[type="button"]',
        'a[href*="signup"]', 'a[href*="register"]', 'a[href*="buy"]', 'a[href*="purchase"]'
    ]
    
    all_ctas = []
    for selector in cta_selectors:
        try:
            elements = soup.select(selector)
            all_ctas.extend(elements)
        except:
            continue
    
    # Remove duplicates
    unique_ctas = []
    seen_texts = set()
    for cta in all_ctas:
        text = cta.get_text().strip().lower()
        if text and text not in seen_texts and len(text) > 2:
            unique_ctas.append(cta)
            seen_texts.add(text)
    
    cta_count = len(unique_ctas)
    cta_data['total_ctas'] = cta_count
    cta_data['cta_texts'] = [cta.get_text().strip() for cta in unique_ctas[:10]]
    
    # Check for invisible/hidden CTAs
    invisible_ctas = 0
    for cta in unique_ctas:
        style = cta.get('style', '')
        classes = ' '.join(cta.get('class', []))
        
        if ('display:none' in style.replace(' ', '') or 
            'visibility:hidden' in style.replace(' ', '') or
            'hidden' in classes or 'invisible' in classes):
            invisible_ctas += 1
    
    cta_data['invisible_ctas'] = invisible_ctas
    
    # Analyze CTA text quality
    weak_cta_words = ['click here', 'learn more', 'read more', 'more info', 'submit']
    strong_cta_words = ['get', 'start', 'try', 'buy', 'download', 'signup', 'join', 'discover']
    
    weak_ctas = 0
    strong_ctas = 0
    
    for cta in unique_ctas:
        text = cta.get_text().strip().lower()
        if any(weak in text for weak in weak_cta_words):
            weak_ctas += 1
        if any(strong in text for strong in strong_cta_words):
            strong_ctas += 1
    
    cta_data['weak_ctas'] = weak_ctas
    cta_data['strong_ctas'] = strong_ctas
    
    # Check for pricing-related elements
    pricing_indicators = soup.select('[class*="price"], [class*="cost"], [id*="price"]')
    pricing_indicators.extend(soup.find_all(text=re.compile(r'\$\d+|\€\d+|£\d+')))
    
    cta_data['has_pricing'] = len(pricing_indicators) > 0
    
    # Check for FAQ section
    faq_indicators = soup.select('[class*="faq"], [id*="faq"]')
    faq_indicators.extend(soup.find_all(text=re.compile(r'FAQ|frequently asked|questions', re.IGNORECASE)))
    
    cta_data['has_faq'] = len(faq_indicators) > 0
    
    return cta_data, cta_issues

def detect_ux_patterns(soup, cta_data, text_content, heading_data, meta_data):
    """Detect specific UX patterns and conversion risks using rule-based logic"""
    ux_patterns = []
    conversion_risks = 0
    
    # Rule 1: Invisible CTA + Complex Text → Layout + Copy Issue
    complex_text = len(text_content.split()) > 1000  # More than 1000 words
    avg_sentence_length = len(text_content.split()) / max(len(text_content.split('.')), 1)
    text_is_complex = avg_sentence_length > 20
    
    if cta_data.get('invisible_ctas', 0) > 0 and (complex_text or text_is_complex):
        conversion_risks += 1
        ux_patterns.append({
            "pattern": "layout_copy_issue",
            "severity": "high",
            "title": "Layout + Copy Issue Detected",
            "description": "Hidden CTAs combined with complex text creates poor user experience",
            "impact": "Users can't find actions and struggle to understand content",
            "fix": "Make CTAs visible and simplify content language",
            "evidence": {
                "invisible_ctas": cta_data.get('invisible_ctas', 0),
                "avg_sentence_length": round(avg_sentence_length, 1),
                "word_count": len(text_content.split())
            }
        })
    
    # Rule 2: Tiny Pricing Text + No FAQ → Conversion Risk
    has_small_text = "font-size" in str(soup).lower() and any(size in str(soup).lower() for size in ["8px", "9px", "10px", "11px", "12px"])
    has_pricing = cta_data.get('has_pricing', False)
    has_faq = cta_data.get('has_faq', False)
    
    if has_pricing and not has_faq and has_small_text:
        conversion_risks += 1
        ux_patterns.append({
            "pattern": "pricing_transparency_risk", 
            "severity": "high",
            "title": "Pricing Transparency Risk",
            "description": "Small pricing text without FAQ section reduces trust and conversions",
            "impact": "Users may abandon due to unclear pricing or terms",
            "fix": "Add FAQ section and ensure pricing is clearly readable",
            "evidence": {
                "has_pricing": has_pricing,
                "has_faq": has_faq,
                "has_small_text": has_small_text
            }
        })
    
    # Rule 3: No Primary CTA + Multiple Weak CTAs → Decision Paralysis
    total_ctas = cta_data.get('total_ctas', 0)
    weak_ctas = cta_data.get('weak_ctas', 0)
    strong_ctas = cta_data.get('strong_ctas', 0)
    
    if total_ctas > 5 and weak_ctas > strong_ctas:
        conversion_risks += 1
        ux_patterns.append({
            "pattern": "decision_paralysis",
            "severity": "medium", 
            "title": "Decision Paralysis Risk",
            "description": "Too many weak CTAs without clear primary action",
            "impact": "Users don't know which action to take, reducing conversions",
            "fix": "Identify one primary CTA and use stronger, action-oriented language",
            "evidence": {
                "total_ctas": total_ctas,
                "weak_ctas": weak_ctas,
                "strong_ctas": strong_ctas,
                "cta_texts": cta_data.get('cta_texts', [])[:5]
            }
        })
    
    # Rule 4: Missing H1 + No Meta Description → SEO + UX Issue
    h1_missing = any(issue.get('element') == 'H1 Tag' for issue in heading_data)
    meta_desc_missing = any(issue.get('element') == 'Meta Description' for issue in meta_data)
    
    if h1_missing and meta_desc_missing:
        conversion_risks += 1
        ux_patterns.append({
            "pattern": "seo_ux_disconnect",
            "severity": "high",
            "title": "SEO + UX Disconnect", 
            "description": "Missing H1 and meta description hurts both search visibility and user understanding",
            "impact": "Lower search rankings and confused users who land on the page",
            "fix": "Add clear H1 heading and compelling meta description",
            "evidence": {
                "h1_missing": h1_missing,
                "meta_desc_missing": meta_desc_missing
            }
        })
    
    # Rule 5: Long Form + No Progress Indicator → Abandonment Risk  
    forms = soup.find_all('form')
    long_forms = [form for form in forms if len(form.find_all(['input', 'textarea', 'select'])) > 5]
    has_progress = bool(soup.select('[class*="progress"], [class*="step"]'))
    
    if len(long_forms) > 0 and not has_progress:
        conversion_risks += 1
        ux_patterns.append({
            "pattern": "form_abandonment_risk",
            "severity": "medium",
            "title": "Form Abandonment Risk",
            "description": "Long forms without progress indicators increase abandonment",
            "impact": "Users abandon forms when they don't know how much is left",
            "fix": "Add progress indicators or break form into steps",
            "evidence": {
                "long_forms": len(long_forms),
                "has_progress": has_progress,
                "max_form_fields": max([len(form.find_all(['input', 'textarea', 'select'])) for form in forms], default=0)
            }
        })
    
    return ux_patterns, conversion_risks

def calculate_clarity_score(visual_score, text_score, heading_score, meta_score, ux_patterns, conversion_risks):
    """Calculate comprehensive clarity score combining all factors"""
    
    # Base score from individual components
    base_score = (
        visual_score * 0.25 +      # Visual/accessibility
        text_score * 0.25 +       # Content readability
        heading_score * 0.20 +    # Structure/SEO
        meta_score * 0.15         # Meta tags/SEO
    )
    
    # UX pattern penalties
    pattern_penalty = 0
    for pattern in ux_patterns:
        if pattern['severity'] == 'high':
            pattern_penalty += 15
        elif pattern['severity'] == 'medium':
            pattern_penalty += 8
        else:
            pattern_penalty += 4
    
    # Conversion risk penalties
    conversion_penalty = conversion_risks * 10  # 10 points per conversion risk
    
    # Apply penalties
    clarity_score = base_score - pattern_penalty - conversion_penalty
    
    # Ensure score is within bounds
    clarity_score = max(0, min(100, clarity_score))
    
    # Bonus for excellent combinations
    if visual_score > 85 and text_score > 85 and len(ux_patterns) == 0:
        clarity_score = min(100, clarity_score + 5)  # Excellence bonus
    
    return clarity_score

async def capture_website_screenshot(url: str):
    """Capture a screenshot of the website using Playwright"""
    try:
        logger.info(f"Starting screenshot capture for {url}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set viewport size for consistent screenshots
            await page.set_viewport_size({"width": 1200, "height": 800})
            
            # Navigate to the website
            await page.goto(str(url), wait_until="domcontentloaded", timeout=10000)
            
            # Wait a bit for content to load
            await page.wait_for_timeout(2000)
            
            # Take screenshot - attempting full page first, fallback to viewport
            try:
                screenshot_bytes = await page.screenshot(
                    type="png",
                    full_page=True  # Try full page
                )
                logger.info(f"Full-page screenshot captured: {len(screenshot_bytes)} bytes")
            except:
                screenshot_bytes = await page.screenshot(
                    type="png",
                    full_page=False  # Fallback to viewport
                )
                logger.info(f"Viewport screenshot captured: {len(screenshot_bytes)} bytes")
            
            await browser.close()
            
            # Convert to base64 for embedding in response
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            screenshot_data_url = f"data:image/png;base64,{screenshot_base64}"
            
            return screenshot_data_url
            
    except Exception as e:
        logger.warning(f"Failed to capture screenshot for {url}: {str(e)}")
        return ""

# Website type detection functions removed - feature discontinued due to accuracy issues

async def analyze_website_simple(url: str):
    """Enhanced website analysis with heading and meta tag analysis"""
    logger.info(f"Analyzing: {url}")
    
    start_time = time.time()
    
    try:
        # Temporarily disable screenshot due to timeout issues - focus on full HTML analysis
        # screenshot_task = capture_website_screenshot(url)
        screenshot_url = ""  # Disable for now
        
        # Fetch website with better headers to bypass Cloudflare
        timeout = aiohttp.ClientTimeout(total=15)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',  # Removed 'br' to avoid brotli issues
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(str(url), headers=headers) as response:
                html_content = await response.text()
        
        # Screenshot disabled for now
        # screenshot_url = await screenshot_task
        
        # Parse HTML - this contains the complete static HTML
        # The screenshot process also triggers dynamic content loading
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Analyze heading structure
        heading_issues, heading_recommendations, heading_score = analyze_heading_structure(soup)
        
        # Analyze meta tags
        meta_issues, meta_recommendations, meta_score = analyze_meta_tags(soup)
        
        # Analyze CTA elements
        cta_data, cta_issues = analyze_cta_elements(soup)
        
        # Remove scripts and styles for text analysis
        for script in soup(["script", "style"]):
            script.decompose()
        
        text_content = soup.get_text()
        clean_text = ' '.join(text_content.split())
        
        # Comprehensive content analysis for full page
        word_count = len(clean_text.split())
        
        # Analyze all images throughout the page
        img_tags = soup.find_all('img')
        img_no_alt = [img for img in img_tags if not img.get('alt', '').strip()]
        
        # Count lazy-loaded images (data-src, data-lazy, etc.)
        lazy_img_tags = soup.find_all('img', attrs={'data-src': True}) + soup.find_all('img', attrs={'data-lazy': True})
        
        # Analyze full page structure
        sections = soup.find_all(['section', 'article', 'main', 'div'])
        footer_content = soup.find_all(['footer'])
        header_content = soup.find_all(['header', 'nav'])
        
        logger.info(f"Full page analysis: {len(img_tags)} images, {len(sections)} sections, {word_count} words")
        
        # Calculate scores
        content_score = 85
        accessibility_score = 90
        
        # Adjust scores based on content
        if word_count < 100:
            content_score -= 20
        elif word_count > 3000:
            content_score += 5
            
        sentences = clean_text.split('.')
        if len(sentences) > 0:
            avg_sentence_length = word_count / len(sentences)
            if avg_sentence_length > 25:
                content_score -= 15
                
        # Adjust accessibility score
        if len(img_no_alt) > 0:
            accessibility_score -= min(25, len(img_no_alt) * 4)
        
        # Weight the final scores
        visual_score = (heading_score * 0.4 + meta_score * 0.3 + accessibility_score * 0.3)
        text_score = content_score
        
        visual_score = max(0, min(100, visual_score))
        text_score = max(0, min(100, text_score))
        
        # Detect UX patterns and conversion risks
        ux_patterns, conversion_risks = detect_ux_patterns(soup, cta_data, clean_text, heading_issues, meta_issues)
        
        # Calculate comprehensive clarity score
        clarity_score = calculate_clarity_score(visual_score, text_score, heading_score, meta_score, ux_patterns, conversion_risks)
        
        # Overall score combines traditional scoring with clarity insights
        overall_score = (visual_score * 0.4 + text_score * 0.3 + clarity_score * 0.3)
        
        # Categorize issues into visual and text/SEO
        visual_issues = []
        text_seo_issues = []
        
        # Add accessibility issues (visual category)
        if len(img_no_alt) > 0:
            visual_issues.append({
                "type": "accessibility",
                "severity": "medium", 
                "message": f"{len(img_no_alt)} images missing alt text",
                "element": "Image Accessibility",
                "suggestion": "Add descriptive alt text to all images"
            })
        
        # Add content issues (text/SEO category)
        if word_count < 100:
            text_seo_issues.append({
                "type": "content",
                "severity": "medium",
                "message": "Very little text content",
                "element": "Content Volume",
                "suggestion": "Add more substantial content for better SEO"
            })
        
        # Add CTA issues to visual category
        visual_issues.extend(cta_issues)
        
        # Add heading and meta issues to text/SEO category
        text_seo_issues.extend(heading_issues + meta_issues)
        
        # Categorize recommendations
        visual_recommendations = []
        text_seo_recommendations = []
        
        if len(img_no_alt) > 0:
            visual_recommendations.append({
                "category": "Accessibility", 
                "priority": "Medium",
                "action": "Add Alt Text",
                "description": "Add descriptive alt text to all images for screen readers"
            })
        
        # Split recommendations by category
        for rec in heading_recommendations + meta_recommendations:
            if rec["category"] in ["SEO", "Structure"]:
                text_seo_recommendations.append(rec)
            else:
                visual_recommendations.append(rec)
        
        # Combine all issues for total count
        all_issues = visual_issues + text_seo_issues
            
        analysis_time = time.time() - start_time
        
        # Determine grade
        if overall_score >= 90: grade = "A+"
        elif overall_score >= 85: grade = "A"  
        elif overall_score >= 80: grade = "A-"
        elif overall_score >= 75: grade = "B+"
        elif overall_score >= 70: grade = "B"
        elif overall_score >= 65: grade = "B-"
        elif overall_score >= 60: grade = "C+"
        elif overall_score >= 55: grade = "C"
        else: grade = "D"
        
        domain = str(url).replace('https://', '').replace('http://', '').split('/')[0]
        
        # Create comprehensive summary with UX insights
        if clarity_score >= 90 and len(ux_patterns) == 0:
            summary = f"{domain} shows excellent clarity with no UX issues - users can easily navigate and convert"
        elif clarity_score >= 80:
            summary = f"{domain} has good clarity with minor UX improvements needed for optimal conversions"
        elif len(ux_patterns) > 0 and conversion_risks > 1:
            pattern_names = [p['pattern'].replace('_', ' ') for p in ux_patterns[:2]]
            summary = f"{domain} has {conversion_risks} conversion risks including {', '.join(pattern_names)} affecting user experience"
        elif clarity_score >= 60:
            summary = f"{domain} needs clarity improvements in structure, content, or user experience design"
        else:
            summary = f"{domain} has significant clarity and conversion issues requiring immediate UX attention"
        
        return {
            "overall_score": round(overall_score, 1),
            "visual_score": round(visual_score, 1), 
            "text_score": round(text_score, 1),
            "clarity_score": round(clarity_score, 1),
            "grade": grade,
            "summary": summary,
            "screenshot_url": screenshot_url,
            "total_issues": len(all_issues),
            "critical_issues": len([i for i in all_issues if i['severity'] == 'high']),
            "conversion_risks": conversion_risks,
            "ux_patterns": ux_patterns,
            "visual_issues": visual_issues,
            "visual_recommendations": visual_recommendations,
            "text_seo_issues": text_seo_issues,
            "text_seo_recommendations": text_seo_recommendations,
            "analysis_time": round(analysis_time, 2),
            "url_analyzed": str(url)
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/v1/analyze/quick", response_model=QuickAnalysisResponse)
async def quick_analysis(request: AnalysisRequest):
    """Perform real website analysis"""
    result = await analyze_website_simple(str(request.url))
    return QuickAnalysisResponse(**result)

if __name__ == "__main__":
    import uvicorn
    print("Starting ClarityCheck REAL Analysis API...")
    print("Real website fetching and analysis enabled")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")