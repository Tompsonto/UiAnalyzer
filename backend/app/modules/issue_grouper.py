"""
Issue Grouping Module
Groups related issues by their parent DOM elements for cleaner analysis presentation
"""

import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import logging
from app.modules.intelligent_grouper import group_issues_intelligently

logger = logging.getLogger(__name__)


@dataclass
class IssueDetail:
    """Individual issue within a group"""
    element: str
    type: str
    severity: str
    message: str
    suggestion: str
    original_issue: Dict[str, Any]


@dataclass
class GroupedIssue:
    """Group of related issues under a common parent"""
    parent_selector: str
    parent_description: str
    severity: str  # highest severity from child issues
    issue_types: List[str]  # unique issue types
    issue_count: int
    details: List[IssueDetail] = field(default_factory=list)
    bbox: Optional[Dict[str, float]] = None
    summary_message: str = ""
    grouped_suggestions: List[str] = field(default_factory=list)


class IssueGrouper:
    """Groups issues by parent elements for cleaner presentation"""
    
    def __init__(self):
        self.severity_weights = {'high': 3, 'medium': 2, 'low': 1}
    
    def group_issues(
        self, 
        visual_issues: List[Dict[str, Any]] = None,
        accessibility_issues: List[Dict[str, Any]] = None,
        cta_issues: List[Dict[str, Any]] = None,
        text_issues: List[Dict[str, Any]] = None
    ) -> List[GroupedIssue]:
        """
        Group all types of issues by their parent elements
        
        Args:
            visual_issues: List of visual analysis issues
            accessibility_issues: List of accessibility issues
            cta_issues: List of CTA analysis issues
            text_issues: List of text analysis issues
            
        Returns:
            List of grouped issues
        """
        all_issues = []
        
        # Collect all issues with their source type
        if visual_issues:
            for issue in visual_issues:
                issue['source'] = 'visual'
                all_issues.append(issue)
        
        if accessibility_issues:
            for issue in accessibility_issues:
                issue['source'] = 'accessibility'
                all_issues.append(issue)
        
        if cta_issues:
            for issue in cta_issues:
                issue['source'] = 'cta'
                all_issues.append(issue)
        
        if text_issues:
            for issue in text_issues:
                issue['source'] = 'text'
                all_issues.append(issue)
        
        if not all_issues:
            return []
        
        # Group issues by parent elements
        issue_groups = self._group_by_parent(all_issues)
        
        # Convert to GroupedIssue objects
        grouped_issues = []
        for parent_selector, issues in issue_groups.items():
            grouped_issue = self._create_grouped_issue(parent_selector, issues)
            grouped_issues.append(grouped_issue)
        
        # Sort by severity and issue count
        grouped_issues.sort(key=lambda x: (
            -self.severity_weights.get(x.severity, 0),
            -x.issue_count
        ))
        
        return grouped_issues
    
    def _group_by_parent(self, issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group issues by their parent elements"""
        groups = defaultdict(list)
        
        for issue in issues:
            element = issue.get('element', 'unknown')
            parent_selector = self._extract_parent_selector(element)
            groups[parent_selector].append(issue)
        
        # If we have many single-issue groups, try to group them further
        return self._consolidate_small_groups(dict(groups))
    
    def _extract_parent_selector(self, selector: str) -> str:
        """Extract parent selector from a CSS selector"""
        if not selector or selector == 'unknown':
            return 'page'
        
        # Handle different selector formats
        try:
            # Remove pseudo-selectors like :nth-of-type(1)
            clean_selector = re.sub(r':nth.*?\)', '', selector)
            clean_selector = re.sub(r':nth-.*?$', '', clean_selector)
            
            # Split by spaces (descendant selectors)
            parts = clean_selector.strip().split()
            if len(parts) > 1:
                # Return the parent (all but last element)
                return ' '.join(parts[:-1])
            
            # If single element, try to find meaningful parent
            if clean_selector.startswith('body'):
                return 'body'
            elif any(tag in clean_selector.lower() for tag in ['header', 'nav', 'main', 'footer', 'section', 'article']):
                # These are likely parent containers
                return clean_selector
            elif '.' in clean_selector or '#' in clean_selector:
                # Has class or ID, likely a container
                return clean_selector
            else:
                # Generic element, group by tag name
                tag_match = re.match(r'^(\w+)', clean_selector)
                if tag_match:
                    tag = tag_match.group(1)
                    if tag in ['div', 'section', 'article', 'header', 'footer', 'nav', 'main']:
                        return tag
                    else:
                        return f'{tag}_container'
                
            return clean_selector
            
        except Exception as e:
            logger.warning(f"Error parsing selector '{selector}': {e}")
            return 'page'
    
    def _consolidate_small_groups(self, groups: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Consolidate groups with single issues into larger semantic groups"""
        consolidated = {}
        semantic_groups = defaultdict(list)
        
        for parent_selector, issues in groups.items():
            if len(issues) >= 2:
                # Keep groups with multiple issues
                consolidated[parent_selector] = issues
            else:
                # Try to group single issues semantically
                semantic_key = self._get_semantic_group(parent_selector, issues[0])
                semantic_groups[semantic_key].append((parent_selector, issues[0]))
        
        # Convert semantic groups back
        for semantic_key, items in semantic_groups.items():
            if len(items) >= 2:
                # Group them under semantic parent
                consolidated[semantic_key] = [item[1] for item in items]
            else:
                # Keep as individual
                parent_selector, issue = items[0]
                consolidated[parent_selector] = [issue]
        
        return consolidated
    
    def _get_semantic_group(self, selector: str, issue: Dict[str, Any]) -> str:
        """Get semantic group for an issue"""
        issue_type = issue.get('type', 'unknown')
        source = issue.get('source', 'unknown')
        
        # Group by issue type and context
        if source == 'accessibility':
            if issue_type in ['contrast', 'alt', 'label']:
                return 'accessibility_content_issues'
            elif issue_type in ['landmark', 'structure']:
                return 'accessibility_structure_issues'
            else:
                return 'accessibility_issues'
        
        elif source == 'visual':
            if issue_type in ['typography', 'contrast']:
                return 'text_visual_issues'
            elif issue_type in ['tap_target', 'overlap']:
                return 'layout_issues'
            else:
                return 'visual_design_issues'
        
        elif source == 'cta':
            return 'conversion_optimization'
        
        elif source == 'text':
            return 'content_issues'
        
        # Fallback to selector-based grouping
        if any(tag in selector.lower() for tag in ['header', 'nav']):
            return 'navigation_area'
        elif any(tag in selector.lower() for tag in ['footer']):
            return 'footer_area'
        elif any(tag in selector.lower() for tag in ['main', 'content', 'article']):
            return 'main_content_area'
        else:
            return 'general_page_issues'
    
    def _create_grouped_issue(self, parent_selector: str, issues: List[Dict[str, Any]]) -> GroupedIssue:
        """Create a GroupedIssue from a list of related issues"""
        
        # Extract details for each issue
        details = []
        severities = []
        issue_types = set()
        sources = set()
        
        for issue in issues:
            detail = IssueDetail(
                element=issue.get('element', 'unknown'),
                type=issue.get('type', 'unknown'),
                severity=issue.get('severity', 'medium'),
                message=issue.get('message', ''),
                suggestion=issue.get('suggestion', ''),
                original_issue=issue
            )
            details.append(detail)
            severities.append(issue.get('severity', 'medium'))
            issue_types.add(issue.get('type', 'unknown'))
            sources.add(issue.get('source', 'unknown'))
        
        # Determine overall severity (highest)
        severity_order = ['high', 'medium', 'low']
        overall_severity = 'low'
        for sev in severity_order:
            if sev in severities:
                overall_severity = sev
                break
        
        # Create parent description
        parent_description = self._create_parent_description(parent_selector, sources)
        
        # Create summary message
        summary_message = self._create_summary_message(parent_selector, details, sources)
        
        # Create grouped suggestions
        grouped_suggestions = self._create_grouped_suggestions(details, sources)
        
        # Extract bbox if available (use first available bbox)
        bbox = None
        for issue in issues:
            if issue.get('bbox'):
                bbox = issue['bbox']
                break
        
        return GroupedIssue(
            parent_selector=parent_selector,
            parent_description=parent_description,
            severity=overall_severity,
            issue_types=list(issue_types),
            issue_count=len(issues),
            details=details,
            bbox=bbox,
            summary_message=summary_message,
            grouped_suggestions=grouped_suggestions
        )
    
    def _create_parent_description(self, parent_selector: str, sources: Set[str]) -> str:
        """Create human-readable description of the parent element"""
        
        # Handle semantic groups
        semantic_descriptions = {
            'accessibility_content_issues': 'Content Accessibility',
            'accessibility_structure_issues': 'Page Structure',
            'text_visual_issues': 'Text & Typography',
            'layout_issues': 'Layout & Interaction',
            'visual_design_issues': 'Visual Design',
            'conversion_optimization': 'Call-to-Action Elements',
            'content_issues': 'Content Quality',
            'navigation_area': 'Navigation Area',
            'footer_area': 'Footer Area', 
            'main_content_area': 'Main Content Area',
            'general_page_issues': 'General Page Issues'
        }
        
        if parent_selector in semantic_descriptions:
            return semantic_descriptions[parent_selector]
        
        # Handle specific selectors
        if parent_selector == 'body':
            return 'Page Body'
        elif parent_selector == 'page':
            return 'Overall Page'
        elif 'header' in parent_selector.lower():
            return 'Header Section'
        elif 'nav' in parent_selector.lower():
            return 'Navigation Menu'
        elif 'footer' in parent_selector.lower():
            return 'Footer Section'
        elif 'main' in parent_selector.lower():
            return 'Main Content'
        elif parent_selector.startswith('.'):
            class_name = parent_selector[1:].replace('-', ' ').replace('_', ' ').title()
            return f'{class_name} Section'
        elif parent_selector.startswith('#'):
            id_name = parent_selector[1:].replace('-', ' ').replace('_', ' ').title()
            return f'{id_name} Area'
        else:
            # Clean up selector for display
            clean = parent_selector.replace('_container', '').replace('_', ' ').title()
            return f'{clean} Elements'
    
    def _create_summary_message(self, parent_selector: str, details: List[IssueDetail], sources: Set[str]) -> str:
        """Create summary message for the grouped issue"""
        
        issue_count = len(details)
        source_types = len(sources)
        
        # Count by severity
        high_count = sum(1 for d in details if d.severity == 'high')
        medium_count = sum(1 for d in details if d.severity == 'medium')
        low_count = sum(1 for d in details if d.severity == 'low')
        
        # Create severity description
        severity_parts = []
        if high_count > 0:
            severity_parts.append(f"{high_count} critical")
        if medium_count > 0:
            severity_parts.append(f"{medium_count} moderate")
        if low_count > 0:
            severity_parts.append(f"{low_count} minor")
        
        severity_desc = " and ".join(severity_parts) if severity_parts else "multiple"
        
        # Create source description
        source_desc = ""
        if 'accessibility' in sources and 'visual' in sources:
            source_desc = "accessibility and visual design"
        elif 'accessibility' in sources:
            source_desc = "accessibility"
        elif 'visual' in sources and 'cta' in sources:
            source_desc = "visual design and conversion"
        elif 'visual' in sources:
            source_desc = "visual design"
        elif 'cta' in sources:
            source_desc = "conversion optimization"
        elif 'text' in sources:
            source_desc = "content quality"
        else:
            source_desc = "usability"
        
        return f"Found {severity_desc} {source_desc} issues affecting user experience"
    
    def _create_grouped_suggestions(self, details: List[IssueDetail], sources: Set[str]) -> List[str]:
        """Create prioritized suggestions for the group"""
        
        suggestions = []
        
        # Priority order for suggestions
        if 'accessibility' in sources:
            suggestions.append("Review accessibility compliance - ensure content is usable by all users")
        
        if 'visual' in sources:
            if any('contrast' in d.type for d in details):
                suggestions.append("Improve color contrast for better readability")
            if any('typography' in d.type for d in details):
                suggestions.append("Optimize text sizing and spacing for better legibility")
        
        if 'cta' in sources:
            suggestions.append("Enhance call-to-action elements for better conversion rates")
        
        if 'text' in sources:
            suggestions.append("Simplify content structure and language for broader audience")
        
        # Add specific high-priority suggestions
        high_issues = [d for d in details if d.severity == 'high']
        if high_issues:
            critical_types = set(d.type for d in high_issues)
            if 'contrast' in critical_types:
                suggestions.insert(0, "URGENT: Fix color contrast issues to meet accessibility standards")
        
        return suggestions[:3]  # Limit to top 3 suggestions


def group_all_issues(
    visual_issues: List[Dict[str, Any]] = None,
    accessibility_issues: List[Dict[str, Any]] = None, 
    cta_issues: List[Dict[str, Any]] = None,
    text_issues: List[Dict[str, Any]] = None
) -> List[GroupedIssue]:
    """Convenience function to group all issue types (legacy method)"""
    grouper = IssueGrouper()
    return grouper.group_issues(visual_issues, accessibility_issues, cta_issues, text_issues)


def group_all_issues_intelligently(
    visual_issues: List[Dict[str, Any]] = None,
    accessibility_issues: List[Dict[str, Any]] = None, 
    cta_issues: List[Dict[str, Any]] = None,
    text_issues: List[Dict[str, Any]] = None,
    dom_content: str = None,
    element_bounding_boxes: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Intelligently group all issue types by meaningful parent elements
    
    Args:
        visual_issues: List of visual analysis issues
        accessibility_issues: List of accessibility issues
        cta_issues: List of CTA analysis issues  
        text_issues: List of text/SEO issues
        dom_content: HTML DOM content for parent detection
        element_bounding_boxes: Element positioning data
        
    Returns:
        List of intelligently grouped issues
    """
    logger.info("Starting intelligent issue grouping")
    
    # Combine all issues into a single list with source tracking
    all_issues = []
    
    if visual_issues:
        for issue in visual_issues:
            issue_copy = issue.copy()
            issue_copy['source'] = 'visual'
            all_issues.append(issue_copy)
    
    if accessibility_issues:
        for issue in accessibility_issues:
            issue_copy = issue.copy()
            issue_copy['source'] = 'accessibility'  
            all_issues.append(issue_copy)
            
    if cta_issues:
        for issue in cta_issues:
            issue_copy = issue.copy()
            issue_copy['source'] = 'cta'
            all_issues.append(issue_copy)
            
    if text_issues:
        for issue in text_issues:
            issue_copy = issue.copy()
            issue_copy['source'] = 'text'
            all_issues.append(issue_copy)
    
    if not all_issues:
        logger.info("No issues to group")
        return []
    
    logger.info(f"Grouping {len(all_issues)} total issues from all sources")
    
    # Use intelligent grouping if DOM content is available
    if dom_content:
        try:
            return group_issues_intelligently(all_issues, dom_content, element_bounding_boxes)
        except Exception as e:
            logger.error(f"Intelligent grouping failed, falling back to legacy method: {e}")
            # Fall back to legacy grouping
            pass
    
    # Fallback to legacy grouping method
    logger.info("Using legacy grouping method")
    grouper = IssueGrouper()
    grouped_issues = grouper.group_issues(visual_issues, accessibility_issues, cta_issues, text_issues)
    
    # Convert legacy format to API format for compatibility
    api_groups = []
    for group in grouped_issues:
        api_group = {
            'parent_selector': group.parent_selector,
            'parent_description': group.parent_description,
            'parent_type': 'generic_content',
            'severity': group.severity,
            'issue_count': group.issue_count,
            'summary_message': group.summary_message,
            'content_summary': f"Contains {len(group.details)} issues",
            'impact_score': len(group.details) * 2,  # Simple scoring
            'details': [
                {
                    'message': detail.message,
                    'element': detail.element,
                    'severity': detail.severity,
                    'source': detail.type,
                    'suggestion': detail.suggestion
                }
                for detail in group.details
            ],
            'grouped_suggestions': group.grouped_suggestions
        }
        api_groups.append(api_group)
    
    return api_groups