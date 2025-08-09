"""
Enhanced Visual Clarity Analysis Module - Advanced HTML/CSS parsing with WCAG compliance
"""
import re
import math
from typing import Dict, List, Any, Tuple, Optional, Union
import logging
from bs4 import BeautifulSoup, Tag
import tinycss2
from wcag_contrast_ratio import rgb, passes_AA, passes_AAA
from colour import Color
import json

logger = logging.getLogger(__name__)

class AdvancedVisualAnalyzer:
    """Advanced visual analysis with WCAG compliance and layout heuristics"""
    
    def __init__(self):
        self.issues = []
        self.score_components = {}
        self.viewport_height = 1080  # Standard desktop viewport
        
        # WCAG contrast thresholds
        self.CONTRAST_THRESHOLDS = {
            'AAA_normal': 7.0,
            'AA_normal': 4.5,
            'AAA_large': 4.5,
            'AA_large': 3.0
        }
        
        # Font size thresholds (in pixels)
        self.FONT_THRESHOLDS = {
            'minimum': 12,
            'small': 14,
            'normal': 16,
            'large': 18
        }
    
    def analyze_visual_clarity(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive visual analysis with HTML/CSS parsing
        """
        self.issues = []
        self.score_components = {}
        
        try:
            logger.info("Starting enhanced visual clarity analysis")
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(page_data.get('html_content', ''), 'html.parser')
            
            # Analyze different visual aspects
            contrast_score = self._analyze_wcag_contrast(page_data, soup)
            typography_score = self._analyze_typography_detailed(page_data, soup)
            cta_score = self._analyze_cta_visibility_advanced(page_data, soup)
            layout_score = self._analyze_layout_heuristics(page_data, soup)
            spacing_score = self._analyze_spacing_density(page_data, soup)
            accessibility_score = self._analyze_visual_accessibility(page_data, soup)
            
            # Calculate weighted overall score
            weights = {
                'contrast': 0.25,
                'typography': 0.20,
                'cta_visibility': 0.20,
                'layout': 0.15,
                'spacing': 0.10,
                'accessibility': 0.10
            }
            
            visual_score = (
                contrast_score * weights['contrast'] +
                typography_score * weights['typography'] +
                cta_score * weights['cta_visibility'] +
                layout_score * weights['layout'] +
                spacing_score * weights['spacing'] +
                accessibility_score * weights['accessibility']
            )
            
            return {
                'visual_score': round(visual_score, 1),
                'score_breakdown': {
                    'contrast': contrast_score,
                    'typography': typography_score,
                    'cta_visibility': cta_score,
                    'layout': layout_score,
                    'spacing': spacing_score,
                    'accessibility': accessibility_score
                },
                'issues': self.issues,
                'recommendations': self._generate_advanced_recommendations(),
                'wcag_compliance': self._get_wcag_compliance_summary(),
                'visual_metrics': self._get_visual_metrics(page_data, soup)
            }
            
        except Exception as e:
            logger.error(f"Enhanced visual analysis error: {str(e)}", exc_info=True)
            return {
                'visual_score': 0,
                'score_breakdown': {},
                'issues': [{'type': 'error', 'severity': 'high', 'message': f'Analysis failed: {str(e)}'}],
                'recommendations': [],
                'wcag_compliance': {'level': 'FAIL', 'issues': 1}
            }
    
    def _analyze_wcag_contrast(self, page_data: Dict[str, Any], soup: BeautifulSoup) -> float:
        """Advanced WCAG contrast analysis using wcag-contrast-ratio library"""
        score = 100
        contrast_issues = 0
        
        # Analyze CTAs with computed styles
        ctas = page_data.get('dom_analysis', {}).get('ctas', [])
        computed_styles = page_data.get('computed_styles', {})
        
        logger.info(f"Analyzing contrast for {len(ctas)} CTAs")
        
        for i, cta in enumerate(ctas[:10]):  # Check top 10 CTAs
            try:
                styles = cta.get('styles', {})
                bg_color = styles.get('backgroundColor', 'rgb(255, 255, 255)')
                text_color = styles.get('color', 'rgb(0, 0, 0)')
                font_size = self._parse_font_size(styles.get('fontSize', '16px'))
                
                # Parse colors
                bg_rgb = self._parse_color_to_rgb(bg_color)
                text_rgb = self._parse_color_to_rgb(text_color)
                
                if bg_rgb and text_rgb:
                    # Calculate contrast ratio using WCAG library
                    contrast_ratio = self._calculate_wcag_contrast(bg_rgb, text_rgb)
                    is_large_text = font_size >= 18 or (font_size >= 14 and 'bold' in styles.get('fontWeight', '').lower())
                    
                    # Determine WCAG compliance
                    aa_threshold = 3.0 if is_large_text else 4.5
                    aaa_threshold = 4.5 if is_large_text else 7.0
                    
                    if contrast_ratio < aa_threshold:
                        severity = 'high' if contrast_ratio < 3.0 else 'medium'
                        score -= 15 if severity == 'high' else 10
                        contrast_issues += 1
                        
                        self.issues.append({
                            'type': 'contrast',
                            'severity': severity,
                            'element': f'CTA: "{cta.get("text", "Unknown")[:30]}"',
                            'message': f'Contrast ratio {contrast_ratio:.2f} fails WCAG AA ({aa_threshold}:1)',
                            'suggestion': f'Increase contrast to at least {aa_threshold}:1 for WCAG AA compliance',
                            'colors': {'background': bg_color, 'text': text_color},
                            'position': cta.get('position', {}),
                            'wcag_level': 'FAIL',
                            'is_large_text': is_large_text
                        })
                    elif contrast_ratio < aaa_threshold:
                        self.issues.append({
                            'type': 'contrast',
                            'severity': 'low',
                            'element': f'CTA: "{cta.get("text", "Unknown")[:30]}"',
                            'message': f'Contrast ratio {contrast_ratio:.2f} meets AA but not AAA',
                            'suggestion': f'Consider increasing contrast to {aaa_threshold}:1 for WCAG AAA',
                            'colors': {'background': bg_color, 'text': text_color},
                            'wcag_level': 'AA',
                            'is_large_text': is_large_text
                        })
                        
            except Exception as e:
                logger.warning(f"Error analyzing contrast for CTA {i}: {str(e)}")
                continue
        
        # Analyze headings contrast
        headings = page_data.get('dom_analysis', {}).get('headings', [])
        for heading in headings[:5]:  # Check top 5 headings
            try:
                # Use computed styles if available
                selector = heading.get('tag', 'h1').lower()
                styles = computed_styles.get(selector, {})
                
                if styles:
                    bg_color = styles.get('backgroundColor', 'rgb(255, 255, 255)')
                    text_color = styles.get('color', 'rgb(0, 0, 0)')
                    
                    bg_rgb = self._parse_color_to_rgb(bg_color)
                    text_rgb = self._parse_color_to_rgb(text_color)
                    
                    if bg_rgb and text_rgb:
                        contrast_ratio = self._calculate_wcag_contrast(bg_rgb, text_rgb)
                        
                        if contrast_ratio < 4.5:  # Headings should meet normal text AA
                            score -= 8
                            contrast_issues += 1
                            
                            self.issues.append({
                                'type': 'contrast',
                                'severity': 'medium',
                                'element': f'Heading: "{heading.get("text", "Unknown")[:40]}"',
                                'message': f'Heading contrast {contrast_ratio:.2f} below AA standard',
                                'suggestion': 'Improve heading text contrast for better readability',
                                'colors': {'background': bg_color, 'text': text_color},
                                'wcag_level': 'FAIL'
                            })
                            
            except Exception as e:
                logger.warning(f"Error analyzing heading contrast: {str(e)}")
                continue
        
        return max(0, score)
    
    def _analyze_typography_detailed(self, page_data: Dict[str, Any], soup: BeautifulSoup) -> float:
        """Detailed typography analysis including font sizes and readability"""
        score = 100
        font_issues = 0
        
        # Analyze CSS for font-size declarations
        css_data = page_data.get('css_data', [])
        computed_styles = page_data.get('computed_styles', {})
        
        small_fonts = []
        font_sizes = []
        
        # Parse CSS rules for font sizes
        for css_rule in css_data:
            if isinstance(css_rule, dict) and 'css_text' in css_rule:
                css_text = css_rule.get('css_text', '')
                font_matches = re.findall(r'font-size:\s*([0-9.]+)(px|pt|em|rem|%)', css_text)
                
                for size_str, unit in font_matches:
                    try:
                        size_px = self._convert_to_pixels(float(size_str), unit)
                        font_sizes.append(size_px)
                        
                        if size_px < self.FONT_THRESHOLDS['small']:
                            small_fonts.append({
                                'size_px': size_px,
                                'original': f"{size_str}{unit}",
                                'selector': css_rule.get('selector', 'unknown')
                            })
                    except (ValueError, TypeError):
                        continue
        
        # Check computed styles for font sizes
        for selector, styles in computed_styles.items():
            font_size = styles.get('fontSize', '')
            if font_size:
                try:
                    size_px = self._parse_font_size(font_size)
                    if size_px and size_px < self.FONT_THRESHOLDS['small']:
                        small_fonts.append({
                            'size_px': size_px,
                            'original': font_size,
                            'selector': selector
                        })
                except:
                    continue
        
        # Penalize small fonts
        if len(small_fonts) > 3:
            score -= 25
            font_issues += len(small_fonts)
            
            self.issues.append({
                'type': 'typography',
                'severity': 'high',
                'element': 'Font Sizes',
                'message': f'{len(small_fonts)} elements with small fonts (<14px) detected',
                'suggestion': 'Increase font sizes to minimum 14px for better readability',
                'details': small_fonts[:5],  # Show first 5 examples
                'count': len(small_fonts)
            })
        elif len(small_fonts) > 0:
            score -= 10
            font_issues += len(small_fonts)
            
            self.issues.append({
                'type': 'typography',
                'severity': 'medium',
                'element': 'Font Sizes',
                'message': f'{len(small_fonts)} elements with small fonts detected',
                'suggestion': 'Consider increasing font sizes for better accessibility',
                'details': small_fonts
            })
        
        # Check font consistency
        if font_sizes:
            unique_sizes = len(set(font_sizes))
            if unique_sizes > 10:  # Too many different font sizes
                score -= 15
                self.issues.append({
                    'type': 'typography',
                    'severity': 'medium',
                    'element': 'Font Consistency',
                    'message': f'{unique_sizes} different font sizes detected',
                    'suggestion': 'Reduce number of font sizes for better visual hierarchy',
                    'font_sizes': sorted(list(set(font_sizes)))[:10]
                })
        
        # Analyze line height
        line_height_issues = self._analyze_line_height(computed_styles)
        score -= line_height_issues * 5
        
        return max(0, score)
    
    def _analyze_cta_visibility_advanced(self, page_data: Dict[str, Any], soup: BeautifulSoup) -> float:
        """Advanced CTA visibility analysis with positioning and prominence"""
        score = 100
        ctas = page_data.get('dom_analysis', {}).get('ctas', [])
        
        if not ctas:
            score -= 30
            self.issues.append({
                'type': 'cta_visibility',
                'severity': 'high',
                'element': 'CTAs',
                'message': 'No call-to-action buttons detected',
                'suggestion': 'Add clear call-to-action buttons to guide users'
            })
            return score
        
        # Check above-fold CTAs
        above_fold_ctas = [cta for cta in ctas if cta.get('above_fold', False)]
        
        if not above_fold_ctas:
            score -= 25
            self.issues.append({
                'type': 'cta_visibility',
                'severity': 'high',
                'element': 'Primary CTA',
                'message': 'No CTAs visible above the fold',
                'suggestion': 'Place primary CTA in the visible area without scrolling'
            })
        
        # Analyze CTA prominence and styling
        for i, cta in enumerate(ctas[:5]):
            try:
                styles = cta.get('styles', {})
                position = cta.get('position', {})
                
                # Check CTA size
                width = position.get('width', 0)
                height = position.get('height', 0)
                
                if width < 80 or height < 35:  # Too small for easy clicking
                    score -= 8
                    self.issues.append({
                        'type': 'cta_visibility',
                        'severity': 'medium',
                        'element': f'CTA: "{cta.get("text", "Unknown")[:20]}"',
                        'message': f'CTA too small ({width}x{height}px)',
                        'suggestion': 'Make CTAs at least 80x35px for easy interaction',
                        'dimensions': {'width': width, 'height': height}
                    })
                
                # Check CTA text length
                text = cta.get('text', '')
                if len(text) > 25:
                    score -= 5
                    self.issues.append({
                        'type': 'cta_visibility',
                        'severity': 'low',
                        'element': f'CTA Text',
                        'message': f'CTA text too long ({len(text)} characters)',
                        'suggestion': 'Keep CTA text under 25 characters',
                        'text': text
                    })
                
                # Check for primary CTA identification
                is_primary = cta.get('is_primary', False)
                if i == 0 and not is_primary and above_fold_ctas:
                    # First CTA should ideally be marked as primary
                    self.issues.append({
                        'type': 'cta_visibility',
                        'severity': 'low',
                        'element': 'Primary CTA',
                        'message': 'Primary CTA not clearly identified',
                        'suggestion': 'Use primary styling classes for main CTA'
                    })
                    
            except Exception as e:
                logger.warning(f"Error analyzing CTA {i}: {str(e)}")
                continue
        
        # Check CTA distribution
        if len(ctas) > 8:
            score -= 15
            self.issues.append({
                'type': 'cta_visibility',
                'severity': 'medium',
                'element': 'CTA Count',
                'message': f'Too many CTAs ({len(ctas)}) may confuse users',
                'suggestion': 'Limit to 3-5 main CTAs for better focus',
                'count': len(ctas)
            })
        
        return max(0, score)
    
    def _analyze_layout_heuristics(self, page_data: Dict[str, Any], soup: BeautifulSoup) -> float:
        """Advanced layout analysis using heuristics"""
        score = 100
        
        # Check DOM structure complexity
        total_elements = len(soup.find_all())
        if total_elements > 500:
            score -= 15
            self.issues.append({
                'type': 'layout',
                'severity': 'medium',
                'element': 'DOM Complexity',
                'message': f'High DOM complexity ({total_elements} elements)',
                'suggestion': 'Simplify page structure to improve performance',
                'element_count': total_elements
            })
        
        # Check nesting depth
        max_depth = self._calculate_max_nesting_depth(soup)
        if max_depth > 12:
            score -= 10
            self.issues.append({
                'type': 'layout',
                'severity': 'low',
                'element': 'Nesting Depth',
                'message': f'Excessive nesting depth ({max_depth} levels)',
                'suggestion': 'Reduce HTML nesting for better maintainability',
                'max_depth': max_depth
            })
        
        # Analyze grid/layout systems
        layout_score = self._analyze_layout_systems(soup)
        score += layout_score  # Bonus for good layout systems
        
        # Check for responsive design indicators
        responsive_score = self._analyze_responsive_indicators(page_data, soup)
        score += responsive_score  # Bonus for responsive design
        
        return min(100, max(0, score))  # Cap at 100
    
    def _analyze_spacing_density(self, page_data: Dict[str, Any], soup: BeautifulSoup) -> float:
        """Analyze spacing and visual density"""
        score = 100
        computed_styles = page_data.get('computed_styles', {})
        
        # Check for adequate padding/margins
        cramped_elements = 0
        
        for selector, styles in computed_styles.items():
            try:
                padding = styles.get('padding', '0')
                margin = styles.get('margin', '0')
                
                # Parse padding values
                padding_values = self._parse_spacing_values(padding)
                margin_values = self._parse_spacing_values(margin)
                
                # Check if element has minimal spacing
                min_padding = min(padding_values) if padding_values else 0
                min_margin = min(margin_values) if margin_values else 0
                
                if min_padding < 8 and min_margin < 8:  # Less than 8px spacing
                    cramped_elements += 1
                    
            except Exception as e:
                continue
        
        if cramped_elements > 5:
            score -= 20
            self.issues.append({
                'type': 'spacing',
                'severity': 'medium',
                'element': 'Layout Spacing',
                'message': f'{cramped_elements} elements with insufficient spacing',
                'suggestion': 'Add adequate padding/margin (minimum 8px) between elements'
            })
        
        # Check content density using images and text
        dom_analysis = page_data.get('dom_analysis', {})
        images = dom_analysis.get('images', [])
        text_length = len(page_data.get('text_content', ''))
        
        if len(images) > 20 and text_length > 5000:
            score -= 15
            self.issues.append({
                'type': 'spacing',
                'severity': 'medium',
                'element': 'Content Density',
                'message': 'High content density may overwhelm users',
                'suggestion': 'Break up content with whitespace and visual hierarchy'
            })
        
        return max(0, score)
    
    def _analyze_visual_accessibility(self, page_data: Dict[str, Any], soup: BeautifulSoup) -> float:
        """Analyze visual accessibility aspects"""
        score = 100
        
        # Check images without alt text
        images = page_data.get('dom_analysis', {}).get('images', [])
        images_no_alt = [img for img in images if not img.get('alt', '').strip()]
        
        if images_no_alt:
            penalty = min(20, len(images_no_alt) * 3)
            score -= penalty
            self.issues.append({
                'type': 'accessibility',
                'severity': 'high',
                'element': 'Image Alt Text',
                'message': f'{len(images_no_alt)} images missing alt text',
                'suggestion': 'Add descriptive alt text to all images',
                'count': len(images_no_alt)
            })
        
        # Check for focus indicators
        css_data = page_data.get('css_data', [])
        has_focus_styles = any(
            ':focus' in rule.get('css_text', '') 
            for rule in css_data 
            if isinstance(rule, dict)
        )
        
        if not has_focus_styles:
            score -= 15
            self.issues.append({
                'type': 'accessibility',
                'severity': 'medium',
                'element': 'Focus Indicators',
                'message': 'No focus styles detected in CSS',
                'suggestion': 'Add visible focus indicators for keyboard navigation'
            })
        
        return max(0, score)
    
    # Helper methods for color and contrast analysis
    def _parse_color_to_rgb(self, color_str: str) -> Optional[Tuple[int, int, int]]:
        """Parse color string to RGB tuple"""
        try:
            # Handle rgb() format
            rgb_match = re.search(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_str)
            if rgb_match:
                return tuple(map(int, rgb_match.groups()))
            
            # Handle rgba() format
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
            
            # Handle named colors using colour library
            if color_str.lower() in ['white', 'black', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta']:
                color = Color(color_str.lower())
                return tuple(int(c * 255) for c in color.rgb)
                
        except Exception as e:
            logger.warning(f"Failed to parse color '{color_str}': {str(e)}")
            
        return None
    
    def _calculate_wcag_contrast(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """Calculate WCAG contrast ratio"""
        try:
            # Use wcag-contrast-ratio library for accurate calculation
            rgb1 = rgb(color1[0], color1[1], color1[2])
            rgb2 = rgb(color2[0], color2[1], color2[2])
            
            return rgb1.contrast_ratio_against(rgb2)
        except Exception as e:
            logger.warning(f"Failed to calculate contrast: {str(e)}")
            return 4.5  # Default to acceptable ratio
    
    def _parse_font_size(self, font_size_str: str) -> Optional[float]:
        """Parse font size string to pixels"""
        try:
            match = re.search(r'([0-9.]+)(px|pt|em|rem|%)?', font_size_str)
            if match:
                size = float(match.group(1))
                unit = match.group(2) or 'px'
                return self._convert_to_pixels(size, unit)
        except:
            pass
        return None
    
    def _convert_to_pixels(self, size: float, unit: str) -> float:
        """Convert font size to pixels"""
        if unit == 'px':
            return size
        elif unit == 'pt':
            return size * 1.33333
        elif unit == 'em' or unit == 'rem':
            return size * 16  # Assuming 16px base
        elif unit == '%':
            return (size / 100) * 16  # Assuming 16px base
        else:
            return size  # Default to pixels
    
    def _analyze_line_height(self, computed_styles: Dict[str, Any]) -> int:
        """Analyze line height for readability"""
        issues = 0
        
        for selector, styles in computed_styles.items():
            line_height = styles.get('lineHeight', '')
            font_size = styles.get('fontSize', '')
            
            if line_height and font_size:
                try:
                    lh_value = self._parse_line_height(line_height, font_size)
                    if lh_value and lh_value < 1.2:  # Too tight
                        issues += 1
                        self.issues.append({
                            'type': 'typography',
                            'severity': 'low',
                            'element': f'Line Height ({selector})',
                            'message': f'Line height {lh_value:.1f} is too tight',
                            'suggestion': 'Use line height of 1.4-1.6 for better readability'
                        })
                except:
                    continue
                    
        return issues
    
    def _parse_line_height(self, line_height: str, font_size: str) -> Optional[float]:
        """Parse line height relative to font size"""
        try:
            if line_height == 'normal':
                return 1.2
            
            if 'px' in line_height:
                lh_px = float(re.search(r'([0-9.]+)', line_height).group(1))
                fs_px = self._parse_font_size(font_size) or 16
                return lh_px / fs_px
            elif '%' in line_height:
                return float(re.search(r'([0-9.]+)', line_height).group(1)) / 100
            else:
                # Unitless value
                return float(line_height)
        except:
            return None
    
    def _calculate_max_nesting_depth(self, soup: BeautifulSoup) -> int:
        """Calculate maximum nesting depth in DOM"""
        def get_depth(element, current_depth=0):
            if not hasattr(element, 'children'):
                return current_depth
            
            max_child_depth = current_depth
            for child in element.children:
                if hasattr(child, 'name'):  # Skip text nodes
                    child_depth = get_depth(child, current_depth + 1)
                    max_child_depth = max(max_child_depth, child_depth)
            
            return max_child_depth
        
        return get_depth(soup.body) if soup.body else 0
    
    def _analyze_layout_systems(self, soup: BeautifulSoup) -> int:
        """Analyze use of modern layout systems (CSS Grid, Flexbox)"""
        bonus = 0
        
        # Look for CSS Grid and Flexbox usage in class names
        grid_classes = soup.find_all(class_=re.compile(r'grid|container|row|col'))
        flex_classes = soup.find_all(class_=re.compile(r'flex|d-flex'))
        
        if grid_classes:
            bonus += 5
        if flex_classes:
            bonus += 5
        
        return bonus
    
    def _analyze_responsive_indicators(self, page_data: Dict[str, Any], soup: BeautifulSoup) -> int:
        """Check for responsive design indicators"""
        bonus = 0
        
        # Check viewport meta tag
        viewport_meta = soup.find('meta', {'name': 'viewport'})
        if viewport_meta:
            bonus += 10
        
        # Check for responsive images
        responsive_imgs = soup.find_all('img', class_=re.compile(r'responsive|img-responsive'))
        if responsive_imgs:
            bonus += 5
        
        return bonus
    
    def _parse_spacing_values(self, spacing_str: str) -> List[float]:
        """Parse CSS spacing values (padding/margin)"""
        try:
            values = []
            # Match all numeric values with units
            matches = re.findall(r'([0-9.]+)(px|em|rem|%)?', spacing_str)
            
            for value_str, unit in matches:
                px_value = self._convert_to_pixels(float(value_str), unit or 'px')
                values.append(px_value)
            
            return values
        except:
            return []
    
    def _get_wcag_compliance_summary(self) -> Dict[str, Any]:
        """Generate WCAG compliance summary"""
        contrast_issues = [issue for issue in self.issues if issue['type'] == 'contrast']
        accessibility_issues = [issue for issue in self.issues if issue['type'] == 'accessibility']
        
        high_contrast_issues = len([i for i in contrast_issues if i.get('severity') == 'high'])
        total_issues = len(contrast_issues) + len(accessibility_issues)
        
        if high_contrast_issues > 0:
            level = 'FAIL'
        elif len(contrast_issues) > 0:
            level = 'AA'
        else:
            level = 'AAA'
        
        return {
            'level': level,
            'contrast_issues': len(contrast_issues),
            'accessibility_issues': len(accessibility_issues),
            'total_issues': total_issues,
            'high_priority_issues': high_contrast_issues
        }
    
    def _get_visual_metrics(self, page_data: Dict[str, Any], soup: BeautifulSoup) -> Dict[str, Any]:
        """Get comprehensive visual metrics"""
        dom_analysis = page_data.get('dom_analysis', {})
        computed_styles = page_data.get('computed_styles', {})
        
        return {
            'total_elements': len(soup.find_all()),
            'cta_count': len(dom_analysis.get('ctas', [])),
            'above_fold_ctas': len([cta for cta in dom_analysis.get('ctas', []) if cta.get('above_fold', False)]),
            'image_count': len(dom_analysis.get('images', [])),
            'heading_count': len(dom_analysis.get('headings', [])),
            'form_count': len(dom_analysis.get('forms', [])),
            'stylesheet_count': page_data.get('stylesheet_count', 0),
            'computed_styles_count': len(computed_styles),
            'max_nesting_depth': self._calculate_max_nesting_depth(soup)
        }
    
    def _generate_advanced_recommendations(self) -> List[Dict[str, str]]:
        """Generate advanced recommendations based on issues"""
        recommendations = []
        issue_types = [issue['type'] for issue in self.issues]
        issue_severities = [issue['severity'] for issue in self.issues]
        
        # High priority recommendations
        if 'contrast' in issue_types:
            high_contrast_issues = len([i for i in self.issues if i['type'] == 'contrast' and i.get('severity') == 'high'])
            recommendations.append({
                'category': 'WCAG Compliance',
                'priority': 'Critical' if high_contrast_issues > 0 else 'High',
                'action': 'Fix Color Contrast Issues',
                'description': f'Resolve {len([i for i in self.issues if i["type"] == "contrast"])} contrast issues to meet WCAG AA standards',
                'impact': 'Accessibility, Legal Compliance',
                'effort': 'Medium'
            })
        
        if 'typography' in issue_types:
            recommendations.append({
                'category': 'Typography',
                'priority': 'High',
                'action': 'Improve Font Sizes',
                'description': 'Increase small fonts to minimum 14px for better readability',
                'impact': 'User Experience, Accessibility',
                'effort': 'Low'
            })
        
        if 'cta_visibility' in issue_types:
            recommendations.append({
                'category': 'Conversion Optimization',
                'priority': 'High',
                'action': 'Optimize CTA Design',
                'description': 'Improve CTA visibility, sizing, and positioning',
                'impact': 'Conversion Rate, User Engagement',
                'effort': 'Medium'
            })
        
        if 'accessibility' in issue_types:
            recommendations.append({
                'category': 'Accessibility',
                'priority': 'High',
                'action': 'Add Missing Alt Text',
                'description': 'Add descriptive alt text to all images',
                'impact': 'Screen Reader Accessibility',
                'effort': 'Low'
            })
        
        if 'spacing' in issue_types:
            recommendations.append({
                'category': 'Layout',
                'priority': 'Medium',
                'action': 'Improve Visual Spacing',
                'description': 'Add adequate whitespace between elements',
                'impact': 'Visual Clarity, Reading Experience',
                'effort': 'Medium'
            })
        
        if 'layout' in issue_types:
            recommendations.append({
                'category': 'Technical',
                'priority': 'Medium',
                'action': 'Simplify DOM Structure',
                'description': 'Reduce HTML complexity and nesting depth',
                'impact': 'Performance, Maintainability',
                'effort': 'High'
            })
        
        return recommendations