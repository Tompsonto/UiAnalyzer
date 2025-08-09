"""
Visual Clarity Analysis Module

This module provides comprehensive visual analysis for web pages, focusing on:
- WCAG contrast compliance 
- Typography issues (font sizes, line heights, line lengths)
- Touch target sizing for mobile
- Element overlap detection
- Visual density analysis
- Layout alignment checks

Author: ClarityCheck Team
Version: 2.0.0
"""

import re
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple, Optional
from bs4 import BeautifulSoup, Tag
from wcag_contrast_ratio import rgb, passes_AA, passes_AAA
import logging

logger = logging.getLogger(__name__)


@dataclass
class Issue:
    """Represents a visual analysis issue"""
    type: str  # contrast, typography, tap_target, overlap, density, alignment
    selector: str
    bbox: Dict[str, float]  # {x, y, width, height}
    severity: str  # high, medium, low
    message: str


@dataclass
class VisualReport:
    """Complete visual analysis report"""
    score: int  # 0-100
    issues: List[Issue] = field(default_factory=list)
    features: Dict[str, Any] = field(default_factory=dict)


def analyze_visual(dom: str, css_snapshot: dict, viewport: tuple[int, int]) -> VisualReport:
    """
    Analyze visual aspects of a web page for clarity and usability.
    
    Args:
        dom: HTML content as string
        css_snapshot: Dictionary containing computed styles and CSS rules
        viewport: Tuple of (width, height) for viewport dimensions
        
    Returns:
        VisualReport with score (0-100), issues list, and feature metrics
    """
    try:
        analyzer = VisualAnalyzer(viewport)
        return analyzer.analyze(dom, css_snapshot)
    except Exception as e:
        logger.error(f"Visual analysis failed: {e}", exc_info=True)
        return VisualReport(
            score=0,
            issues=[Issue(
                type="error",
                selector="body", 
                bbox={"x": 0, "y": 0, "width": 0, "height": 0},
                severity="high",
                message=f"Analysis failed: {str(e)}"
            )]
        )


class VisualAnalyzer:
    """Core visual analysis engine"""
    
    def __init__(self, viewport: tuple[int, int]):
        self.viewport_width, self.viewport_height = viewport
        self.is_mobile = self.viewport_width < 768
        self.issues: List[Issue] = []
        
    def analyze(self, dom: str, css_snapshot: dict) -> VisualReport:
        """Run complete visual analysis"""
        soup = BeautifulSoup(dom, 'html.parser')
        computed_styles = css_snapshot.get('computed_styles', {})
        elements_data = css_snapshot.get('elements', [])
        
        # Reset issues for new analysis
        self.issues = []
        
        # Run all analysis functions
        contrast_score = self._analyze_contrast(soup, computed_styles, elements_data)
        typography_score = self._analyze_typography(soup, computed_styles, elements_data)
        tap_target_score = self._analyze_tap_targets(soup, elements_data)
        overlap_score = self._analyze_overlap(elements_data)
        density_score = self._analyze_density(elements_data)
        alignment_score = self._analyze_alignment(elements_data)
        
        # Calculate weighted overall score
        weights = {
            'contrast': 0.25,
            'typography': 0.20,
            'tap_targets': 0.15,
            'overlap': 0.15,
            'density': 0.15,
            'alignment': 0.10
        }
        
        overall_score = int(
            contrast_score * weights['contrast'] +
            typography_score * weights['typography'] +
            tap_target_score * weights['tap_targets'] +
            overlap_score * weights['overlap'] +
            density_score * weights['density'] +
            alignment_score * weights['alignment']
        )
        
        features = {
            'contrast_score': contrast_score,
            'typography_score': typography_score, 
            'tap_target_score': tap_target_score,
            'overlap_score': overlap_score,
            'density_score': density_score,
            'alignment_score': alignment_score,
            'viewport_width': self.viewport_width,
            'viewport_height': self.viewport_height,
            'is_mobile': self.is_mobile,
            'total_elements': len(elements_data),
            'total_issues': len(self.issues)
        }
        
        return VisualReport(
            score=max(0, min(100, overall_score)),
            issues=self.issues,
            features=features
        )
    
    def _analyze_contrast(self, soup: BeautifulSoup, computed_styles: dict, elements: list) -> float:
        """Analyze WCAG contrast compliance"""
        score = 100.0
        
        for element in elements:
            try:
                # Skip non-text elements
                if not element.get('text', '').strip():
                    continue
                    
                styles = element.get('styles', {})
                bbox = element.get('bbox', {})
                
                # Get colors
                fg_color = self._parse_color(styles.get('color', 'rgb(0,0,0)'))
                bg_color = self._parse_color(styles.get('backgroundColor', 'rgb(255,255,255)'))
                
                if not fg_color or not bg_color:
                    continue
                    
                # Calculate contrast ratio
                contrast_ratio = self._calculate_contrast_ratio(fg_color, bg_color)
                
                # Determine if text is large
                font_size = self._parse_font_size(styles.get('fontSize', '16px'))
                font_weight = styles.get('fontWeight', 'normal')
                is_large = font_size >= 18 or (font_size >= 14 and font_weight in ['bold', '700', '800', '900'])
                
                # WCAG thresholds
                aa_threshold = 3.0 if is_large else 4.5
                aaa_threshold = 4.5 if is_large else 7.0
                
                # Check compliance
                if contrast_ratio < aa_threshold:
                    severity = 'high' if contrast_ratio < 3.0 else 'medium'
                    score -= 15 if severity == 'high' else 10
                    
                    element_desc = self._get_element_description(element.get('selector', 'unknown'))
                    self.issues.append(Issue(
                        type='contrast',
                        selector=element.get('selector', 'unknown'),
                        bbox=bbox,
                        severity=severity,
                        message=f'Poor color contrast on {element_desc} makes text hard to read, especially for users with visual impairments'
                    ))
                elif contrast_ratio < aaa_threshold:
                    score -= 3  # Minor penalty for AAA non-compliance
                    
                    element_desc = self._get_element_description(element.get('selector', 'unknown'))
                    self.issues.append(Issue(
                        type='contrast',
                        selector=element.get('selector', 'unknown'),
                        bbox=bbox,
                        severity='low',
                        message=f'Moderate color contrast on {element_desc} could be improved for better accessibility'
                    ))
                    
            except Exception as e:
                logger.warning(f"Error analyzing contrast for element: {e}")
                continue
                
        return max(0, score)
    
    def _analyze_typography(self, soup: BeautifulSoup, computed_styles: dict, elements: list) -> float:
        """Analyze typography issues"""
        score = 100.0
        
        for element in elements:
            try:
                # Skip non-text elements
                if not element.get('text', '').strip():
                    continue
                    
                styles = element.get('styles', {})
                bbox = element.get('bbox', {})
                text = element.get('text', '')
                
                # Font size analysis
                font_size = self._parse_font_size(styles.get('fontSize', '16px'))
                min_size = 14 if self.is_mobile else 16
                
                if font_size < min_size:
                    severity = 'high' if font_size < 12 else 'medium'
                    score -= 12 if severity == 'high' else 8
                    
                    element_desc = self._get_element_description(element.get('selector', 'unknown'))
                    device = "mobile devices" if self.is_mobile else "desktop screens"
                    self.issues.append(Issue(
                        type='typography',
                        selector=element.get('selector', 'unknown'),
                        bbox=bbox,
                        severity=severity,
                        message=f'Text too small on {element_desc} ({font_size}px) causes reading difficulty on {device}'
                    ))
                
                # Line height analysis
                line_height = self._parse_line_height(styles.get('lineHeight', 'normal'), font_size)
                if line_height and line_height < 1.3:
                    score -= 5
                    
                    element_desc = self._get_element_description(element.get('selector', 'unknown'))
                    self.issues.append(Issue(
                        type='typography',
                        selector=element.get('selector', 'unknown'),
                        bbox=bbox,
                        severity='medium',
                        message=f'Lines too close together on {element_desc} (line-height: {line_height:.1f}) reduces readability'
                    ))
                
                # Line length analysis (approximate)
                if bbox.get('width', 0) > 0 and font_size > 0:
                    chars_per_line = bbox['width'] / (font_size * 0.6)  # Rough estimate
                    if chars_per_line > 90:
                        score -= 5
                        
                        element_desc = self._get_element_description(element.get('selector', 'unknown'))
                        self.issues.append(Issue(
                            type='typography',
                            selector=element.get('selector', 'unknown'),
                            bbox=bbox,
                            severity='low',
                            message=f'Text lines too long on {element_desc} (~{chars_per_line:.0f} characters) makes reading tiring'
                        ))
                        
            except Exception as e:
                logger.warning(f"Error analyzing typography for element: {e}")
                continue
                
        return max(0, score)
    
    def _analyze_tap_targets(self, soup: BeautifulSoup, elements: list) -> float:
        """Analyze tap target sizes for mobile"""
        if not self.is_mobile:
            return 100.0  # Only relevant for mobile
            
        score = 100.0
        
        interactive_selectors = ['a', 'button', 'input', '[onclick]', '[role="button"]']
        
        for element in elements:
            try:
                selector = element.get('selector', '')
                bbox = element.get('bbox', {})
                
                # Check if element is interactive
                is_interactive = any(sel in selector.lower() for sel in interactive_selectors)
                if not is_interactive:
                    continue
                    
                width = bbox.get('width', 0)
                height = bbox.get('height', 0)
                
                # WCAG recommends 44x44px minimum
                if width < 44 or height < 44:
                    severity = 'high' if (width < 32 or height < 32) else 'medium'
                    score -= 15 if severity == 'high' else 10
                    
                    element_desc = self._get_element_description(selector)
                    self.issues.append(Issue(
                        type='tap_target',
                        selector=selector,
                        bbox=bbox,
                        severity=severity,
                        message=f'{element_desc.title()} too small for mobile tapping ({width:.0f}x{height:.0f}px)'
                    ))
                    
            except Exception as e:
                logger.warning(f"Error analyzing tap targets for element: {e}")
                continue
                
        return max(0, score)
    
    def _analyze_overlap(self, elements: list) -> float:
        """Detect overlapping elements"""
        score = 100.0
        checked_pairs = set()
        
        for i, elem1 in enumerate(elements):
            for j, elem2 in enumerate(elements[i+1:], i+1):
                try:
                    # Avoid checking same pair twice
                    pair_key = (min(i, j), max(i, j))
                    if pair_key in checked_pairs:
                        continue
                    checked_pairs.add(pair_key)
                    
                    bbox1 = elem1.get('bbox', {})
                    bbox2 = elem2.get('bbox', {})
                    
                    if self._boxes_overlap(bbox1, bbox2):
                        # Check if it's meaningful overlap (not just touching edges)
                        overlap_area = self._calculate_overlap_area(bbox1, bbox2)
                        min_area = min(bbox1.get('width', 0) * bbox1.get('height', 0),
                                     bbox2.get('width', 0) * bbox2.get('height', 0))
                        
                        if overlap_area > min_area * 0.1:  # 10% overlap threshold
                            score -= 8
                            
                            elem1_desc = self._get_element_description(elem1.get('selector', 'unknown'))
                            elem2_desc = self._get_element_description(elem2.get('selector', 'unknown'))
                            self.issues.append(Issue(
                                type='overlap',
                                selector=f"{elem1.get('selector', 'unknown')} ∩ {elem2.get('selector', 'unknown')}",
                                bbox=bbox1,
                                severity='medium',
                                message=f'Elements overlapping: {elem1_desc} and {elem2_desc} creating visual confusion'
                            ))
                            
                except Exception as e:
                    logger.warning(f"Error analyzing overlap: {e}")
                    continue
                    
        return max(0, score)
    
    def _analyze_density(self, elements: list) -> float:
        """Analyze interactive element density"""
        score = 100.0
        
        # Define regions (1000x800px blocks)
        region_width = 1000
        region_height = 800
        
        regions = {}
        interactive_selectors = ['a', 'button', 'input', '[onclick]', '[role="button"]']
        
        for element in elements:
            try:
                selector = element.get('selector', '')
                bbox = element.get('bbox', {})
                
                # Check if element is interactive
                is_interactive = any(sel in selector.lower() for sel in interactive_selectors)
                if not is_interactive:
                    continue
                    
                x = bbox.get('x', 0)
                y = bbox.get('y', 0)
                
                # Determine which region this element belongs to
                region_x = int(x // region_width)
                region_y = int(y // region_height)
                region_key = (region_x, region_y)
                
                if region_key not in regions:
                    regions[region_key] = []
                regions[region_key].append(element)
                
            except Exception as e:
                logger.warning(f"Error analyzing density for element: {e}")
                continue
        
        # Check each region for high density
        for region_key, region_elements in regions.items():
            if len(region_elements) > 20:
                score -= 15
                
                # Use first element's bbox as representative
                representative_bbox = region_elements[0].get('bbox', {})
                
                self.issues.append(Issue(
                    type='density',
                    selector=f'region_{region_key[0]}_{region_key[1]}',
                    bbox=representative_bbox,
                    severity='medium',
                    message=f'Too many interactive elements clustered together ({len(region_elements)} elements) overwhelming users'
                ))
                
        return max(0, score)
    
    def _analyze_alignment(self, elements: list) -> float:
        """Analyze element alignment in columns"""
        score = 100.0
        
        # Group elements by approximate vertical position (within 20px)
        rows = []
        tolerance = 20
        
        for element in elements:
            try:
                bbox = element.get('bbox', {})
                y = bbox.get('y', 0)
                
                # Find existing row or create new one
                row_found = False
                for row in rows:
                    if abs(row['y'] - y) <= tolerance:
                        row['elements'].append(element)
                        row_found = True
                        break
                
                if not row_found:
                    rows.append({
                        'y': y,
                        'elements': [element]
                    })
                    
            except Exception as e:
                logger.warning(f"Error grouping elements for alignment: {e}")
                continue
        
        # Check alignment within each row
        for row in rows:
            if len(row['elements']) < 3:  # Need at least 3 elements to check alignment
                continue
                
            try:
                left_edges = [elem.get('bbox', {}).get('x', 0) for elem in row['elements']]
                
                # Check for consistent alignment
                if len(set(left_edges)) > 1:  # Not all aligned
                    min_x = min(left_edges)
                    max_deviation = max(abs(x - min_x) for x in left_edges)
                    
                    if max_deviation > 8:  # More than 8px deviation
                        score -= 5
                        
                        # Use first element as representative
                        representative_bbox = row['elements'][0].get('bbox', {})
                        
                        self.issues.append(Issue(
                            type='alignment',
                            selector=f'row_y_{row["y"]:.0f}',
                            bbox=representative_bbox,
                            severity='low',
                            message=f'Elements misaligned in row (deviation: {max_deviation:.0f}px) creating unprofessional appearance'
                        ))
                        
            except Exception as e:
                logger.warning(f"Error analyzing alignment for row: {e}")
                continue
                
        return max(0, score)
    
    # Helper methods
    
    def _get_element_description(self, selector: str) -> str:
        """Convert CSS selector to user-friendly element description"""
        if not selector or selector == 'unknown':
            return "page element"
        
        # Handle specific element types
        if 'h1' in selector.lower():
            return "main heading"
        elif any(h in selector.lower() for h in ['h2', 'h3', 'h4', 'h5', 'h6']):
            return "heading"
        elif 'button' in selector.lower():
            return "button"
        elif 'a' in selector.lower():
            return "link"
        elif 'input' in selector.lower():
            return "form input"
        elif 'p' in selector.lower():
            return "paragraph text"
        elif 'nav' in selector.lower():
            return "navigation menu"
        elif any(cls in selector.lower() for cls in ['btn', 'button', 'cta']):
            return "button/call-to-action"
        else:
            # Extract tag name if possible
            tag_match = re.match(r'^(\w+)', selector.lower())
            if tag_match:
                tag = tag_match.group(1)
                return f"{tag} element"
            return "page element"
    
    def _parse_color(self, color_str: str) -> Optional[Tuple[int, int, int]]:
        """Parse CSS color string to RGB tuple"""
        try:
            # Handle rgb() format
            rgb_match = re.search(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_str)
            if rgb_match:
                return tuple(map(int, rgb_match.groups()))
            
            # Handle rgba() format (ignore alpha)
            rgba_match = re.search(r'rgba\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)', color_str)
            if rgba_match:
                return tuple(map(int, rgba_match.groups()))
            
            # Handle hex format
            hex_match = re.search(r'#([0-9a-fA-F]{6})', color_str)
            if hex_match:
                hex_color = hex_match.group(1)
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Handle 3-digit hex
            hex3_match = re.search(r'#([0-9a-fA-F]{3})', color_str)
            if hex3_match:
                hex_color = hex3_match.group(1)
                return tuple(int(c*2, 16) for c in hex_color)
            
            # Handle named colors
            color_map = {
                'black': (0, 0, 0), 'white': (255, 255, 255),
                'red': (255, 0, 0), 'green': (0, 128, 0), 'blue': (0, 0, 255),
                'yellow': (255, 255, 0), 'cyan': (0, 255, 255), 'magenta': (255, 0, 255)
            }
            return color_map.get(color_str.lower())
            
        except Exception as e:
            logger.warning(f"Failed to parse color '{color_str}': {e}")
            return None
    
    def _calculate_contrast_ratio(self, fg: Tuple[int, int, int], bg: Tuple[int, int, int]) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        try:
            # Use manual calculation as primary method (more reliable)
            return self._calculate_contrast_manual(fg, bg)
        except Exception as e:
            logger.warning(f"Failed to calculate contrast ratio: {e}")
            return 4.5  # Default safe value
    
    def _calculate_contrast_manual(self, fg: Tuple[int, int, int], bg: Tuple[int, int, int]) -> float:
        """Manual WCAG contrast ratio calculation as fallback"""
        def relative_luminance(rgb_tuple):
            """Calculate relative luminance for RGB color"""
            r, g, b = [c / 255.0 for c in rgb_tuple]
            
            # Apply gamma correction
            def gamma_correct(c):
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            
            r = gamma_correct(r)
            g = gamma_correct(g)  
            b = gamma_correct(b)
            
            # Calculate luminance using ITU-R BT.709 coefficients
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        # Calculate luminance for both colors
        l1 = relative_luminance(fg)
        l2 = relative_luminance(bg)
        
        # Ensure lighter color is numerator
        light = max(l1, l2)
        dark = min(l1, l2)
        
        # Calculate contrast ratio
        return (light + 0.05) / (dark + 0.05)
    
    def _parse_font_size(self, font_size_str: str) -> float:
        """Parse font size string to pixels"""
        try:
            match = re.search(r'([0-9.]+)(px|pt|em|rem|%)?', font_size_str)
            if match:
                size = float(match.group(1))
                unit = match.group(2) or 'px'
                
                if unit == 'px':
                    return size
                elif unit == 'pt':
                    return size * 1.33333
                elif unit in ['em', 'rem']:
                    return size * 16  # Assuming 16px base
                elif unit == '%':
                    return (size / 100) * 16  # Assuming 16px base
                    
            return 16.0  # Default
        except:
            return 16.0
    
    def _parse_line_height(self, line_height_str: str, font_size: float) -> Optional[float]:
        """Parse line height relative to font size"""
        try:
            if line_height_str == 'normal':
                return 1.2
            
            if 'px' in line_height_str:
                lh_px = float(re.search(r'([0-9.]+)', line_height_str).group(1))
                return lh_px / font_size
            elif '%' in line_height_str:
                return float(re.search(r'([0-9.]+)', line_height_str).group(1)) / 100
            else:
                # Unitless value
                return float(line_height_str)
        except:
            return None
    
    def _boxes_overlap(self, bbox1: dict, bbox2: dict) -> bool:
        """Check if two bounding boxes overlap"""
        try:
            x1, y1, w1, h1 = bbox1.get('x', 0), bbox1.get('y', 0), bbox1.get('width', 0), bbox1.get('height', 0)
            x2, y2, w2, h2 = bbox2.get('x', 0), bbox2.get('y', 0), bbox2.get('width', 0), bbox2.get('height', 0)
            
            return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)
        except:
            return False
    
    def _calculate_overlap_area(self, bbox1: dict, bbox2: dict) -> float:
        """Calculate overlapping area between two bounding boxes"""
        try:
            x1, y1, w1, h1 = bbox1.get('x', 0), bbox1.get('y', 0), bbox1.get('width', 0), bbox1.get('height', 0)
            x2, y2, w2, h2 = bbox2.get('x', 0), bbox2.get('y', 0), bbox2.get('width', 0), bbox2.get('height', 0)
            
            # Calculate intersection
            left = max(x1, x2)
            top = max(y1, y2)
            right = min(x1 + w1, x2 + w2)
            bottom = min(y1 + h1, y2 + h2)
            
            if left < right and top < bottom:
                return (right - left) * (bottom - top)
            return 0.0
        except:
            return 0.0