"""
Intelligent Issue Grouper - Groups issues by meaningful parent elements
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag
import re

logger = logging.getLogger(__name__)

@dataclass
class ParentContext:
    """Context information about a parent element"""
    element: Tag
    selector: str
    element_type: str  # 'header_section', 'content_section', etc.
    description: str
    semantic_score: float
    content_summary: str
    child_count: int
    bbox: Optional[Dict[str, float]] = None  # Bounding box coordinates

@dataclass
class IntelligentGroup:
    """Intelligently grouped issues with parent context"""
    parent_context: ParentContext
    issues: List[Dict[str, Any]]
    severity: str  # Overall severity for the group
    summary_message: str
    container_suggestions: List[str]  # Container-level fix suggestions
    impact_score: float  # How important this container is

class IntelligentIssueGrouper:
    """
    Intelligently groups issues by finding meaningful parent containers
    rather than just DOM hierarchy
    """
    
    # Parent type classification with semantic weights
    PARENT_TYPES = {
        'header_section': {
            'selectors': ['header', 'div.header', '.navbar', '.nav-bar', '.site-header'],
            'content_types': ['h1', 'h2', 'h3', 'nav', 'logo', 'brand'],
            'weight': 10,
            'description_template': 'Header Section'
        },
        'navigation': {
            'selectors': ['nav', 'div.nav', '.navigation', '.menu', '.nav-menu'],
            'content_types': ['nav', 'ul', 'li', 'a'],
            'weight': 9,
            'description_template': 'Navigation Menu'
        },
        'hero_section': {
            'selectors': ['div.hero', '.hero-section', '.banner', '.jumbotron'],
            'content_types': ['h1', 'h2', 'p', 'button', 'img'],
            'weight': 9,
            'description_template': 'Hero/Banner Section'
        },
        'content_section': {
            'selectors': ['main', 'div.content', '.main-content', 'article', 'section'],
            'content_types': ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'ul', 'ol'],
            'weight': 8,
            'description_template': 'Main Content Section'
        },
        'cta_section': {
            'selectors': ['div.cta', '.call-to-action', '.action-section'],
            'content_types': ['button', 'form', 'input', 'a.btn'],
            'weight': 9,
            'description_template': 'Call-to-Action Section'
        },
        'sidebar': {
            'selectors': ['aside', 'div.sidebar', '.side-bar', '.widget-area'],
            'content_types': ['ul', 'li', 'p', 'h3', 'h4'],
            'weight': 6,
            'description_template': 'Sidebar Section'
        },
        'footer_section': {
            'selectors': ['footer', 'div.footer', '.site-footer'],
            'content_types': ['p', 'ul', 'li', 'a'],
            'weight': 7,
            'description_template': 'Footer Section'
        },
        'form_section': {
            'selectors': ['form', 'div.form', '.form-container', '.contact-form'],
            'content_types': ['input', 'textarea', 'select', 'button', 'label'],
            'weight': 8,
            'description_template': 'Form Section'
        },
        'media_section': {
            'selectors': ['div.gallery', '.media-section', '.image-grid'],
            'content_types': ['img', 'video', 'figure'],
            'weight': 6,
            'description_template': 'Media Gallery'
        },
        'generic_content': {
            'selectors': ['div'],
            'content_types': ['*'],  # Fallback for any content
            'weight': 4,
            'description_template': 'Content Container'
        }
    }
    
    # Content types that make a container semantically meaningful
    SEMANTIC_CONTENT_TYPES = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',  # Headers
        'p', 'span', 'div',                   # Text content
        'img', 'video', 'figure',             # Media
        'ul', 'ol', 'li',                     # Lists
        'button', 'a',                        # Interactive
        'form', 'input', 'textarea',          # Forms
        'nav', 'header', 'footer', 'aside',   # Semantic HTML5
        'article', 'section'                  # Content sections
    ]
    
    def __init__(self):
        self.dom_soup = None
        
    def group_issues_intelligently(
        self, 
        issues: List[Dict[str, Any]], 
        dom_content: str,
        element_bounding_boxes: List[Dict[str, Any]] = None
    ) -> List[IntelligentGroup]:
        """
        Group issues by intelligent parent detection
        
        Args:
            issues: List of issues to group
            dom_content: HTML DOM content
            element_bounding_boxes: Optional element positioning data
            
        Returns:
            List of intelligently grouped issues
        """
        logger.info(f"Starting intelligent grouping for {len(issues)} issues")
        
        # Parse DOM
        self.dom_soup = BeautifulSoup(dom_content, 'html.parser')
        
        # Create element bbox lookup
        bbox_lookup = {}
        if element_bounding_boxes:
            for bbox in element_bounding_boxes:
                selector = bbox.get('selector', '')
                if selector:
                    bbox_lookup[selector] = bbox.get('bbox', {})
        
        # Group issues by parent
        parent_groups = {}
        
        for issue in issues:
            element_selector = issue.get('element', issue.get('selector', ''))
            if not element_selector:
                continue
                
            # Find meaningful parent for this element
            parent_context = self._find_meaningful_parent(element_selector, bbox_lookup)
            
            if parent_context:
                parent_key = parent_context.selector
                if parent_key not in parent_groups:
                    parent_groups[parent_key] = {
                        'parent_context': parent_context,
                        'issues': []
                    }
                parent_groups[parent_key]['issues'].append(issue)
        
        # Convert to IntelligentGroup objects
        intelligent_groups = []
        for parent_key, group_data in parent_groups.items():
            parent_context = group_data['parent_context']
            issues_list = group_data['issues']
            
            # Calculate group-level metrics
            severity = self._calculate_group_severity(issues_list)
            summary_message = self._generate_summary_message(parent_context, issues_list)
            container_suggestions = self._generate_container_suggestions(parent_context, issues_list)
            impact_score = self._calculate_impact_score(parent_context, issues_list)
            
            intelligent_group = IntelligentGroup(
                parent_context=parent_context,
                issues=issues_list,
                severity=severity,
                summary_message=summary_message,
                container_suggestions=container_suggestions,
                impact_score=impact_score
            )
            
            intelligent_groups.append(intelligent_group)
        
        # Sort by impact score (highest first)
        intelligent_groups.sort(key=lambda g: g.impact_score, reverse=True)
        
        logger.info(f"Created {len(intelligent_groups)} intelligent groups")
        return intelligent_groups
    
    def _find_meaningful_parent(
        self, 
        element_selector: str, 
        bbox_lookup: Dict[str, Dict]
    ) -> Optional[ParentContext]:
        """
        Find the most meaningful parent div for an element
        
        Args:
            element_selector: CSS selector of the element
            bbox_lookup: Bounding box data for elements
            
        Returns:
            ParentContext with information about the best parent
        """
        try:
            # Parse selector and find element in DOM
            element = self._find_element_by_selector(element_selector)
            if not element:
                logger.debug(f"Could not find element for selector: {element_selector}")
                return None
            
            # Traverse up the DOM tree to find meaningful parents
            current = element.parent
            best_parent = None
            best_score = 0
            
            # Look up to 10 levels up the DOM tree
            levels_checked = 0
            while current and levels_checked < 10:
                if current.name in ['div', 'section', 'article', 'header', 'footer', 'aside', 'nav', 'main']:
                    score = self._score_parent_element(current)
                    if score > best_score:
                        best_score = score
                        best_parent = current
                
                current = current.parent
                levels_checked += 1
            
            if not best_parent:
                # Fallback to immediate parent if no good div found
                best_parent = element.parent
                if not best_parent:
                    return None
            
            # Create parent context
            parent_selector = self._create_selector_for_element(best_parent)
            element_type = self._classify_parent_type(best_parent)
            description = self._generate_parent_description(best_parent, element_type)
            content_summary = self._summarize_content(best_parent)
            child_count = len(list(best_parent.children))
            bbox = bbox_lookup.get(parent_selector, {})
            
            return ParentContext(
                element=best_parent,
                selector=parent_selector,
                element_type=element_type,
                description=description,
                semantic_score=best_score,
                content_summary=content_summary,
                child_count=child_count,
                bbox=bbox if bbox else None
            )
            
        except Exception as e:
            logger.error(f"Error finding meaningful parent for {element_selector}: {e}")
            return None
    
    def _find_element_by_selector(self, selector: str) -> Optional[Tag]:
        """Find element by CSS selector with fallbacks"""
        try:
            # Try direct CSS selector
            element = self.dom_soup.select_one(selector)
            if element:
                return element
            
            # Try simplified selectors for common patterns
            if '#' in selector:
                # Try just the ID part
                id_part = selector.split('#')[1].split('.')[0].split(' ')[0].split(':')[0]
                element = self.dom_soup.find(id=id_part)
                if element:
                    return element
            
            if '.' in selector:
                # Try just the class part
                class_part = selector.split('.')[1].split(' ')[0].split('#')[0].split(':')[0]
                element = self.dom_soup.find(class_=class_part)
                if element:
                    return element
            
            # Try tag name only
            tag_match = re.match(r'^([a-zA-Z]+)', selector)
            if tag_match:
                tag_name = tag_match.group(1)
                element = self.dom_soup.find(tag_name)
                if element:
                    return element
                    
        except Exception as e:
            logger.debug(f"Error parsing selector {selector}: {e}")
        
        return None
    
    def _score_parent_element(self, element: Tag) -> float:
        """
        Score a potential parent element based on semantic content
        
        Returns:
            Float score (higher = better parent)
        """
        if not element or not hasattr(element, 'name'):
            return 0
        
        score = 0
        
        # Base score by element type
        if element.name == 'div':
            score += 1
        elif element.name in ['section', 'article', 'header', 'footer', 'aside', 'nav', 'main']:
            score += 3  # Semantic HTML5 elements are better
        
        # Score based on attributes (IDs and classes give context)
        if element.get('id'):
            score += 2
        if element.get('class'):
            score += 1
            # Bonus for semantic class names
            classes = ' '.join(element.get('class', []))
            for parent_type, config in self.PARENT_TYPES.items():
                for selector_pattern in config['selectors']:
                    if any(keyword in classes.lower() for keyword in selector_pattern.replace('.', '').replace('div', '').split('-')):
                        score += config['weight'] * 0.1
        
        # Score based on semantic content diversity
        child_tags = [child.name for child in element.find_all() if hasattr(child, 'name')]
        semantic_child_types = set(tag for tag in child_tags if tag in self.SEMANTIC_CONTENT_TYPES)
        
        # Bonus for content diversity (more content types = better container)
        content_diversity = len(semantic_child_types)
        score += content_diversity * 0.5
        
        # Penalty for being too nested or too shallow
        depth = len(list(element.parents))
        if depth < 2:
            score *= 0.8  # Too shallow
        elif depth > 8:
            score *= 0.9  # Too deep
        
        # Bonus for reasonable amount of content
        text_content = element.get_text(strip=True)
        if 20 <= len(text_content) <= 1000:  # Good amount of content
            score += 1
        
        return score
    
    def _classify_parent_type(self, element: Tag) -> str:
        """Classify the type of parent element based on content and attributes"""
        if not element:
            return 'generic_content'
        
        element_html = str(element).lower()
        element_text = element.get_text().lower()
        
        # Check element tag first
        if element.name in ['header']:
            return 'header_section'
        elif element.name in ['nav']:
            return 'navigation'
        elif element.name in ['footer']:
            return 'footer_section'
        elif element.name in ['form']:
            return 'form_section'
        elif element.name in ['aside']:
            return 'sidebar'
        elif element.name in ['main', 'article']:
            return 'content_section'
        
        # Check classes and IDs
        attrs = f"{element.get('class', [])} {element.get('id', '')}"
        attrs_str = ' '.join(attrs).lower()
        
        # Score each parent type
        type_scores = {}
        for parent_type, config in self.PARENT_TYPES.items():
            score = 0
            
            # Check if selector patterns match
            for selector_pattern in config['selectors']:
                pattern_parts = selector_pattern.replace('.', '').replace('div', '').split('-')
                if any(part in attrs_str for part in pattern_parts if part):
                    score += 2
            
            # Check content types
            child_tags = [child.name for child in element.find_all() if hasattr(child, 'name')]
            content_matches = 0
            for content_type in config['content_types']:
                if content_type == '*' or content_type in child_tags:
                    content_matches += 1
            
            score += content_matches * 0.5
            type_scores[parent_type] = score
        
        # Return the highest scoring type
        best_type = max(type_scores.items(), key=lambda x: x[1])
        return best_type[0] if best_type[1] > 0 else 'generic_content'
    
    def _create_selector_for_element(self, element: Tag) -> str:
        """Create a CSS selector for an element"""
        if not element or not hasattr(element, 'name'):
            return 'unknown'
        
        # Prefer ID if available
        if element.get('id'):
            return f"{element.name}#{element.get('id')}"
        
        # Use first class if available
        classes = element.get('class', [])
        if classes:
            return f"{element.name}.{classes[0]}"
        
        # Generate position-based selector
        siblings = [s for s in element.parent.children if hasattr(s, 'name') and s.name == element.name] if element.parent else [element]
        position = siblings.index(element) + 1 if element in siblings else 1
        
        return f"{element.name}:nth-of-type({position})"
    
    def _generate_parent_description(self, element: Tag, element_type: str) -> str:
        """Generate human-readable description for parent element"""
        base_description = self.PARENT_TYPES.get(element_type, {}).get('description_template', 'Content Container')
        
        # Add more specific context if available
        element_id = element.get('id', '')
        classes = element.get('class', [])
        
        if element_id:
            return f"{base_description} ({element_id})"
        elif classes:
            return f"{base_description} ({classes[0]})"
        
        return base_description
    
    def _summarize_content(self, element: Tag) -> str:
        """Summarize the content within an element"""
        if not element:
            return "No content"
        
        child_tags = [child.name for child in element.find_all() if hasattr(child, 'name')]
        tag_counts = {}
        for tag in child_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Create content summary
        content_parts = []
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:4]:
            if tag in self.SEMANTIC_CONTENT_TYPES:
                content_parts.append(f"{count} {tag}" + ("s" if count > 1 else ""))
        
        if content_parts:
            return f"Contains {', '.join(content_parts)}"
        else:
            text_length = len(element.get_text(strip=True))
            return f"Contains {text_length} characters of text"
    
    def _calculate_group_severity(self, issues: List[Dict[str, Any]]) -> str:
        """Calculate overall severity for a group of issues"""
        if not issues:
            return 'low'
        
        severity_weights = {'high': 3, 'medium': 2, 'low': 1}
        total_weight = sum(severity_weights.get(issue.get('severity', 'low'), 1) for issue in issues)
        avg_weight = total_weight / len(issues)
        
        if avg_weight >= 2.5:
            return 'high'
        elif avg_weight >= 1.5:
            return 'medium'
        else:
            return 'low'
    
    def _generate_summary_message(self, parent_context: ParentContext, issues: List[Dict[str, Any]]) -> str:
        """Generate summary message for grouped issues"""
        issue_count = len(issues)
        severity = self._calculate_group_severity(issues)
        
        severity_desc = {
            'high': 'critical issues',
            'medium': 'important issues', 
            'low': 'minor issues'
        }
        
        return f"{parent_context.description} has {issue_count} {severity_desc.get(severity, 'issues')} affecting user experience"
    
    def _generate_container_suggestions(self, parent_context: ParentContext, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate container-level fix suggestions"""
        suggestions = []
        
        # Analyze issue types to generate container-wide suggestions
        issue_types = [issue.get('type', issue.get('message', '').lower()) for issue in issues]
        
        # Common container-level fixes
        if any('contrast' in issue_type for issue_type in issue_types):
            suggestions.append(f"Review color scheme throughout {parent_context.description.lower()}")
        
        if any('accessibility' in issue_type or 'alt' in issue_type for issue_type in issue_types):
            suggestions.append(f"Add accessibility improvements to {parent_context.description.lower()}")
        
        if any('size' in issue_type or 'tap' in issue_type for issue_type in issue_types):
            suggestions.append(f"Optimize interactive element sizes in {parent_context.description.lower()}")
        
        if any('font' in issue_type or 'typography' in issue_type for issue_type in issue_types):
            suggestions.append(f"Establish consistent typography in {parent_context.description.lower()}")
        
        # Default suggestion if no specific patterns found
        if not suggestions:
            suggestions.append(f"Review and improve {parent_context.description.lower()} for better user experience")
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def _calculate_impact_score(self, parent_context: ParentContext, issues: List[Dict[str, Any]]) -> float:
        """Calculate impact score for prioritizing groups"""
        # Base score from parent type weight
        parent_weight = self.PARENT_TYPES.get(parent_context.element_type, {}).get('weight', 4)
        
        # Issue count and severity multiplier
        severity_multipliers = {'high': 3, 'medium': 2, 'low': 1}
        issue_score = sum(severity_multipliers.get(issue.get('severity', 'low'), 1) for issue in issues)
        
        # Semantic score from parent analysis
        semantic_score = parent_context.semantic_score
        
        # Combined impact score
        impact_score = (parent_weight * 2) + (issue_score * 1.5) + semantic_score
        
        return impact_score


# Convenience function for integration
def group_issues_intelligently(
    issues: List[Dict[str, Any]], 
    dom_content: str,
    element_bounding_boxes: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to group issues intelligently
    
    Returns:
        List of grouped issues in API-compatible format
    """
    grouper = IntelligentIssueGrouper()
    intelligent_groups = grouper.group_issues_intelligently(issues, dom_content, element_bounding_boxes)
    
    # Convert to API-compatible format
    api_groups = []
    for group in intelligent_groups:
        api_group = {
            'parent_selector': group.parent_context.selector,
            'parent_description': group.parent_context.description,
            'parent_type': group.parent_context.element_type,
            'severity': group.severity,
            'issue_count': len(group.issues),
            'summary_message': group.summary_message,
            'content_summary': group.parent_context.content_summary,
            'impact_score': group.impact_score,
            'details': [
                {
                    'message': issue.get('message', ''),
                    'element': issue.get('element', issue.get('selector', '')),
                    'severity': issue.get('severity', 'low'),
                    'source': issue.get('source', issue.get('type', 'unknown')),
                    'suggestion': issue.get('suggestion', issue.get('fix', ''))
                }
                for issue in group.issues
            ],
            'grouped_suggestions': group.container_suggestions
        }
        
        # Add bounding box if available
        if group.parent_context.bbox:
            api_group['bbox'] = group.parent_context.bbox
            
        api_groups.append(api_group)
    
    return api_groups