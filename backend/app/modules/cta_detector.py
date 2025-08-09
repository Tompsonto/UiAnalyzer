"""
CTA (Call-to-Action) Discovery and Visibility Analysis
Detects CTAs and analyzes their visibility, accessibility, and effectiveness
"""

import re
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


@dataclass
class CTAIssue:
    """Individual CTA issue"""
    type: str  # visibility, contrast, tap_target, text_clarity, position
    severity: str  # high, medium, low
    message: str
    suggestion: str


@dataclass
class CTAAnalysis:
    """Analysis results for a single CTA"""
    selector: str
    text: str
    element_type: str  # button, link, input
    bbox: Dict[str, float]  # x, y, width, height
    is_primary: bool
    above_fold: bool
    visibility_score: float  # 0-100
    contrast_ratio: Optional[float]
    tap_target_score: float  # 0-100
    text_clarity_score: float  # 0-100
    overall_score: float  # 0-100
    issues: List[CTAIssue] = field(default_factory=list)
    styles: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CTAReport:
    """Complete CTA analysis report"""
    ctas: List[CTAAnalysis] = field(default_factory=list)
    primary_cta: Optional[CTAAnalysis] = None
    total_ctas_found: int = 0
    above_fold_ctas: int = 0
    processing_time: float = 0


class CTADetector:
    """Detects and analyzes Call-to-Action elements"""
    
    # CTA-indicative text patterns
    CTA_PATTERNS = [
        # Action words
        r'\b(buy|purchase|order|shop|get|download|subscribe|signup?|register|join|start|begin|try|learn|discover|explore)\b',
        # Conversion words  
        r'\b(free|now|today|instant|immediate|quick|fast|easy|save|deal|offer|limited|exclusive)\b',
        # Contact words
        r'\b(contact|call|email|book|schedule|request|quote|demo|consultation)\b',
        # Navigation words
        r'\b(continue|next|proceed|submit|send|go|view|see|read|more|all|full)\b'
    ]
    
    # Words that reduce CTA clarity
    JARGON_WORDS = [
        'utilize', 'implement', 'leverage', 'facilitate', 'optimize', 'enhance',
        'strategize', 'synergize', 'paradigm', 'methodology', 'framework',
        'infrastructure', 'scalability', 'ecosystem', 'holistic', 'comprehensive'
    ]
    
    def __init__(self, viewport_width: int = 1440, viewport_height: int = 900):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.fold_position = viewport_height
    
    def detect_ctas(
        self, 
        dom_content: str, 
        element_bounding_boxes: List[Dict[str, Any]], 
        computed_styles: Dict[str, Any]
    ) -> CTAReport:
        """
        Detect and analyze CTAs in the provided DOM and element data
        
        Args:
            dom_content: HTML content
            element_bounding_boxes: List of element bounding boxes with metadata
            computed_styles: Computed CSS styles for elements
            
        Returns:
            CTAReport with detected CTAs and analysis
        """
        import time
        start_time = time.time()
        
        soup = BeautifulSoup(dom_content, 'html.parser')
        cta_analyses = []
        
        # Identify potential CTA elements
        potential_ctas = self._identify_potential_ctas(element_bounding_boxes, computed_styles)
        
        # Analyze each potential CTA
        for cta_data in potential_ctas:
            analysis = self._analyze_single_cta(cta_data, soup)
            if analysis:
                cta_analyses.append(analysis)
        
        # Identify primary CTA
        primary_cta = self._identify_primary_cta(cta_analyses)
        
        # Count above-fold CTAs
        above_fold_count = sum(1 for cta in cta_analyses if cta.above_fold)
        
        report = CTAReport(
            ctas=cta_analyses,
            primary_cta=primary_cta,
            total_ctas_found=len(cta_analyses),
            above_fold_ctas=above_fold_count,
            processing_time=time.time() - start_time
        )
        
        return report
    
    def _identify_potential_ctas(
        self, 
        element_boxes: List[Dict[str, Any]], 
        computed_styles: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify elements that could be CTAs"""
        potential_ctas = []
        
        for element in element_boxes:
            # Skip invisible elements
            if not element.get('visible', False):
                continue
            
            bbox = element.get('bbox', {})
            if bbox.get('width', 0) < 10 or bbox.get('height', 0) < 10:
                continue
            
            selector = element.get('selector', '')
            text = element.get('text', '').strip()
            
            # Check if element looks like a CTA
            is_cta = self._is_potential_cta(selector, text, element, computed_styles)
            
            if is_cta:
                potential_ctas.append(element)
        
        return potential_ctas
    
    def _is_potential_cta(
        self, 
        selector: str, 
        text: str, 
        element: Dict[str, Any], 
        computed_styles: Dict[str, Any]
    ) -> bool:
        """Check if an element is likely a CTA"""
        
        # Check by element type
        if any(tag in selector.lower() for tag in ['button', 'input']):
            return True
        
        # Check by classes/IDs that suggest CTA
        cta_indicators = ['btn', 'button', 'cta', 'call-to-action', 'submit', 'buy', 'purchase', 'download', 'signup', 'register']
        if any(indicator in selector.lower() for indicator in cta_indicators):
            return True
        
        # Check by text content
        if text and len(text) <= 50:  # Reasonable CTA text length
            text_lower = text.lower()
            
            # Check for CTA patterns
            for pattern in self.CTA_PATTERNS:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return True
        
        # Check by styling (buttons often have background colors, borders, etc.)
        element_styles = computed_styles.get(selector, {})
        if element_styles:
            bg_color = element_styles.get('backgroundColor', 'rgba(0, 0, 0, 0)')
            border = element_styles.get('border', 'none')
            padding = element_styles.get('padding', '0px')
            
            # Elements with background colors, borders, or padding are often interactive
            if (bg_color and bg_color not in ['rgba(0, 0, 0, 0)', 'transparent'] or 
                border and border != 'none' or
                padding and padding != '0px'):
                # Additional check: if it has CTA-like text
                if text and any(word in text.lower() for word in ['click', 'buy', 'get', 'start', 'join', 'try']):
                    return True
        
        return False
    
    def _analyze_single_cta(self, cta_data: Dict[str, Any], soup: BeautifulSoup) -> Optional[CTAAnalysis]:
        """Analyze a single CTA element"""
        try:
            selector = cta_data.get('selector', '')
            text = cta_data.get('text', '').strip()
            bbox = cta_data.get('bbox', {})
            
            if not text or not bbox:
                return None
            
            # Determine element type
            element_type = self._get_element_type(selector)
            
            # Position analysis
            above_fold = bbox.get('y', 0) < self.fold_position
            
            # Visibility analysis
            visibility_score, visibility_issues = self._analyze_visibility(cta_data, bbox)
            
            # Contrast analysis
            contrast_ratio, contrast_issues = self._analyze_contrast(cta_data)
            
            # Tap target analysis
            tap_target_score, tap_target_issues = self._analyze_tap_target(bbox)
            
            # Text clarity analysis
            text_clarity_score, text_clarity_issues = self._analyze_text_clarity(text)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                visibility_score, contrast_ratio, tap_target_score, text_clarity_score
            )
            
            # Collect all issues
            all_issues = visibility_issues + contrast_issues + tap_target_issues + text_clarity_issues
            
            analysis = CTAAnalysis(
                selector=selector,
                text=text,
                element_type=element_type,
                bbox=bbox,
                is_primary=False,  # Will be determined later
                above_fold=above_fold,
                visibility_score=visibility_score,
                contrast_ratio=contrast_ratio,
                tap_target_score=tap_target_score,
                text_clarity_score=text_clarity_score,
                overall_score=overall_score,
                issues=all_issues,
                styles=self._extract_relevant_styles(cta_data)
            )
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Error analyzing CTA: {e}")
            return None
    
    def _get_element_type(self, selector: str) -> str:
        """Determine the element type from selector"""
        if 'button' in selector.lower():
            return 'button'
        elif 'input' in selector.lower():
            return 'input'
        elif 'a' in selector.lower():
            return 'link'
        else:
            return 'element'
    
    def _analyze_visibility(self, cta_data: Dict[str, Any], bbox: Dict[str, float]) -> Tuple[float, List[CTAIssue]]:
        """Analyze CTA visibility"""
        score = 100.0
        issues = []
        
        # Check size
        width = bbox.get('width', 0)
        height = bbox.get('height', 0)
        area = width * height
        
        if area < 1000:  # Very small
            score -= 30
            issues.append(CTAIssue(
                type='visibility',
                severity='high',
                message=f'CTA is very small ({width:.0f}x{height:.0f}px) and hard to notice',
                suggestion='Increase CTA size to at least 44x44px with adequate padding'
            ))
        elif area < 2000:  # Small
            score -= 15
            issues.append(CTAIssue(
                type='visibility',
                severity='medium',
                message=f'CTA could be larger ({width:.0f}x{height:.0f}px) for better visibility',
                suggestion='Consider increasing CTA size for better prominence'
            ))
        
        # Check position
        x = bbox.get('x', 0)
        y = bbox.get('y', 0)
        
        # Too far right might be cut off
        if x + width > self.viewport_width * 0.95:
            score -= 20
            issues.append(CTAIssue(
                type='visibility',
                severity='medium',
                message='CTA may be cut off on narrow screens',
                suggestion='Ensure CTA fits within viewport on all screen sizes'
            ))
        
        # Below fold reduces visibility
        if y > self.fold_position:
            score -= 25
            issues.append(CTAIssue(
                type='position',
                severity='medium',
                message='CTA is below the fold and may not be seen immediately',
                suggestion='Consider placing primary CTAs above the fold'
            ))
        
        return max(0, score), issues
    
    def _analyze_contrast(self, cta_data: Dict[str, Any]) -> Tuple[Optional[float], List[CTAIssue]]:
        """Analyze CTA color contrast (basic implementation)"""
        issues = []
        
        # This is a simplified implementation - in a real scenario,
        # you'd need the actual computed colors from the element
        # For now, we'll assume most CTAs have decent contrast
        contrast_ratio = 4.5  # Assume decent contrast
        
        if contrast_ratio < 3.0:
            issues.append(CTAIssue(
                type='contrast',
                severity='high',
                message=f'CTA has poor color contrast ({contrast_ratio:.1f}:1)',
                suggestion='Increase color contrast to at least 4.5:1 for accessibility'
            ))
        elif contrast_ratio < 4.5:
            issues.append(CTAIssue(
                type='contrast', 
                severity='medium',
                message=f'CTA contrast could be improved ({contrast_ratio:.1f}:1)',
                suggestion='Consider increasing contrast for better accessibility'
            ))
        
        return contrast_ratio, issues
    
    def _analyze_tap_target(self, bbox: Dict[str, float]) -> Tuple[float, List[CTAIssue]]:
        """Analyze tap target size"""
        score = 100.0
        issues = []
        
        width = bbox.get('width', 0)
        height = bbox.get('height', 0)
        min_dimension = min(width, height)
        
        # WCAG guidelines suggest 44x44px minimum
        if min_dimension < 32:
            score -= 40
            issues.append(CTAIssue(
                type='tap_target',
                severity='high',
                message=f'CTA too small for easy tapping ({width:.0f}x{height:.0f}px)',
                suggestion='Increase CTA size to at least 44x44px for mobile accessibility'
            ))
        elif min_dimension < 44:
            score -= 20
            issues.append(CTAIssue(
                type='tap_target',
                severity='medium',
                message=f'CTA size could be improved ({width:.0f}x{height:.0f}px)',
                suggestion='Consider increasing to 44x44px for better mobile usability'
            ))
        
        return max(0, score), issues
    
    def _analyze_text_clarity(self, text: str) -> Tuple[float, List[CTAIssue]]:
        """Analyze CTA text clarity"""
        score = 100.0
        issues = []
        
        if not text:
            return 0, [CTAIssue(
                type='text_clarity',
                severity='high',
                message='CTA has no text label',
                suggestion='Add clear, descriptive text to the CTA'
            )]
        
        word_count = len(text.split())
        
        # Word count check
        if word_count > 5:
            score -= 20
            issues.append(CTAIssue(
                type='text_clarity',
                severity='medium',
                message=f'CTA text is long ({word_count} words) and may be unclear',
                suggestion='Keep CTA text to 3-5 words for clarity'
            ))
        
        # Jargon check
        text_lower = text.lower()
        jargon_count = sum(1 for word in self.JARGON_WORDS if word in text_lower)
        if jargon_count > 0:
            score -= 15 * jargon_count
            issues.append(CTAIssue(
                type='text_clarity',
                severity='medium',
                message='CTA contains jargon that may confuse users',
                suggestion='Use simple, clear language that describes the action'
            ))
        
        # Check for action words
        has_action = any(re.search(pattern, text_lower) for pattern in self.CTA_PATTERNS)
        if not has_action:
            score -= 25
            issues.append(CTAIssue(
                type='text_clarity',
                severity='medium',
                message='CTA text doesn\'t clearly indicate the action',
                suggestion='Use action words like "Buy", "Get", "Start", "Download"'
            ))
        
        # Check for vague terms
        vague_terms = ['click here', 'learn more', 'read more', 'click', 'here']
        if any(term in text_lower for term in vague_terms):
            score -= 15
            issues.append(CTAIssue(
                type='text_clarity',
                severity='low',
                message='CTA text is vague and doesn\'t specify the benefit',
                suggestion='Be specific about what happens when clicked'
            ))
        
        return max(0, score), issues
    
    def _calculate_overall_score(
        self, 
        visibility_score: float, 
        contrast_ratio: Optional[float], 
        tap_target_score: float, 
        text_clarity_score: float
    ) -> float:
        """Calculate overall CTA score"""
        
        # Weights for different aspects
        weights = {
            'visibility': 0.3,
            'contrast': 0.2, 
            'tap_target': 0.25,
            'text_clarity': 0.25
        }
        
        # Convert contrast ratio to score
        contrast_score = 100.0
        if contrast_ratio:
            if contrast_ratio < 3.0:
                contrast_score = 40.0
            elif contrast_ratio < 4.5:
                contrast_score = 70.0
            else:
                contrast_score = 100.0
        
        overall = (
            visibility_score * weights['visibility'] +
            contrast_score * weights['contrast'] +
            tap_target_score * weights['tap_target'] +
            text_clarity_score * weights['text_clarity']
        )
        
        return round(overall, 1)
    
    def _extract_relevant_styles(self, cta_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant styling information"""
        return {
            'selector': cta_data.get('selector', ''),
            'bbox': cta_data.get('bbox', {}),
            'visible': cta_data.get('visible', False),
            'above_fold': cta_data.get('above_fold', False)
        }
    
    def _identify_primary_cta(self, cta_analyses: List[CTAAnalysis]) -> Optional[CTAAnalysis]:
        """Identify the primary CTA using heuristics"""
        if not cta_analyses:
            return None
        
        # Score each CTA for primary likelihood
        for cta in cta_analyses:
            primary_score = 0.0
            
            # Position heuristics
            if cta.above_fold:
                primary_score += 30
            
            # Size heuristics  
            area = cta.bbox.get('width', 0) * cta.bbox.get('height', 0)
            if area > 5000:  # Large CTA
                primary_score += 20
            elif area > 3000:  # Medium CTA
                primary_score += 10
            
            # Text heuristics - primary action words
            primary_words = ['buy', 'purchase', 'get started', 'sign up', 'subscribe', 'download', 'try free', 'start trial']
            text_lower = cta.text.lower()
            for word in primary_words:
                if word in text_lower:
                    primary_score += 25
                    break
            
            # Position heuristics - center and top are often primary
            x = cta.bbox.get('x', 0)
            width = cta.bbox.get('width', 0)
            center_x = x + width / 2
            viewport_center = self.viewport_width / 2
            
            if abs(center_x - viewport_center) < viewport_center * 0.3:  # Within 30% of center
                primary_score += 15
            
            # Quality score bonus
            if cta.overall_score > 80:
                primary_score += 15
            elif cta.overall_score > 60:
                primary_score += 10
            
            cta.primary_score = primary_score
        
        # Find highest scoring CTA
        primary_cta = max(cta_analyses, key=lambda x: getattr(x, 'primary_score', 0))
        primary_cta.is_primary = True
        
        return primary_cta


# Convenience function
def detect_ctas(
    dom_content: str, 
    element_bounding_boxes: List[Dict[str, Any]], 
    computed_styles: Dict[str, Any],
    viewport_width: int = 1440,
    viewport_height: int = 900
) -> CTAReport:
    """Convenience function to detect CTAs"""
    detector = CTADetector(viewport_width, viewport_height)
    return detector.detect_ctas(dom_content, element_bounding_boxes, computed_styles)