"""
Selenium-based Accessibility Analysis - Replaces Playwright a11y_runner
"""
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

from app.modules.selenium_renderer import SeleniumRenderer

logger = logging.getLogger(__name__)


@dataclass
class A11yIssueSelenium:
    """Accessibility issue found by axe-core via Selenium"""
    rule_id: str
    description: str
    impact: str  # 'critical', 'serious', 'moderate', 'minor'
    selector: str
    message: str
    help_url: str
    internal_type: str  # Mapped to our internal taxonomy


@dataclass
class A11yReportSelenium:
    """Accessibility analysis report from Selenium + axe-core"""
    issues: List[A11yIssueSelenium]
    total_violations: int
    processing_time: float
    url: str


class SeleniumAccessibilityAnalyzer:
    """Selenium-based accessibility analyzer using axe-core"""
    
    # Map axe rule IDs to our internal taxonomy
    RULE_MAPPING = {
        'color-contrast': 'contrast',
        'color-contrast-enhanced': 'contrast', 
        'landmark-one-main': 'landmark',
        'landmark-main-is-top-level': 'landmark',
        'landmark-no-duplicate-banner': 'landmark',
        'landmark-no-duplicate-contentinfo': 'landmark',
        'landmark-unique': 'landmark',
        'page-has-heading-one': 'structure',
        'heading-order': 'structure',
        'label': 'label',
        'aria-label': 'label',
        'aria-labelledby': 'label',
        'button-name': 'label',
        'link-name': 'label',
        'image-alt': 'alt',
        'input-image-alt': 'alt',
        'area-alt': 'alt',
        'keyboard': 'keyboard',
        'focus-order-semantics': 'keyboard',
        'tabindex': 'keyboard'
    }
    
    def __init__(self, viewport_width: int = 1440, viewport_height: int = 900):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
    
    def run_a11y_analysis(self, url: str) -> A11yReportSelenium:
        """
        Run accessibility analysis on a URL using Selenium + axe-core
        
        Args:
            url: URL to analyze
            
        Returns:
            A11yReportSelenium with accessibility issues
        """
        import time
        start_time = time.time()
        
        try:
            logger.info(f"Starting accessibility analysis for {url}")
            
            # Use Selenium renderer to load page and run axe
            with SeleniumRenderer(self.viewport_width, self.viewport_height) as renderer:
                # Load the page
                renderer.render_website(url)
                
                # Run accessibility scan
                violations = renderer.run_accessibility_scan()
                
                # Process violations into our format
                issues = []
                for violation in violations:
                    issue = self._create_a11y_issue(violation)
                    if issue:
                        issues.append(issue)
                
                processing_time = time.time() - start_time
                
                logger.info(f"Accessibility analysis completed: {len(issues)} issues found in {processing_time:.2f}s")
                
                return A11yReportSelenium(
                    issues=issues,
                    total_violations=len(issues),
                    processing_time=processing_time,
                    url=url
                )
                
        except Exception as e:
            logger.error(f"Accessibility analysis failed for {url}: {e}")
            raise Exception(f"Accessibility analysis failed: {str(e)}")
    
    def _create_a11y_issue(self, violation: Dict[str, Any]) -> A11yIssueSelenium:
        """
        Create A11yIssueSelenium from axe violation
        
        Args:
            violation: Raw violation from axe-selenium-python
            
        Returns:
            A11yIssueSelenium or None if invalid
        """
        try:
            rule_id = violation.get('rule_id', '')
            description = violation.get('description', '')
            impact = violation.get('impact', 'moderate')
            selector = violation.get('selector', '')
            message = violation.get('message', '')
            help_url = violation.get('help_url', '')
            
            # Map to internal taxonomy
            internal_type = self.RULE_MAPPING.get(rule_id, 'other')
            
            # Clean up message
            if not message:
                message = description
                
            # Ensure we have required fields
            if not rule_id or not description:
                logger.debug(f"Skipping invalid violation: {violation}")
                return None
            
            return A11yIssueSelenium(
                rule_id=rule_id,
                description=description,
                impact=impact,
                selector=selector,
                message=self._improve_message(message, internal_type),
                help_url=help_url,
                internal_type=internal_type
            )
            
        except Exception as e:
            logger.debug(f"Error creating A11y issue from {violation}: {e}")
            return None
    
    def _improve_message(self, message: str, internal_type: str) -> str:
        """
        Improve accessibility messages to be more user-friendly
        
        Args:
            message: Original axe message
            internal_type: Our internal issue type
            
        Returns:
            Improved message string
        """
        if internal_type == 'contrast':
            return "Text doesn't have enough contrast with its background, making it hard to read"
        elif internal_type == 'landmark':
            return "Page structure is missing important navigation landmarks for screen readers"
        elif internal_type == 'structure':
            return "Page heading structure doesn't follow proper hierarchy"
        elif internal_type == 'label':
            return "Interactive element is missing a descriptive label for screen readers"
        elif internal_type == 'alt':
            return "Image is missing alternative text description"
        elif internal_type == 'keyboard':
            return "Element cannot be properly accessed using keyboard navigation"
        else:
            # Return original message but ensure it's user-friendly
            if len(message) > 100:
                return message[:100] + "..."
            return message


# Convenience function for API compatibility
async def run_a11y_selenium(url: str) -> A11yReportSelenium:
    """
    Convenience function to run accessibility analysis with Selenium
    
    Maintains API compatibility with the Playwright version
    """
    analyzer = SeleniumAccessibilityAnalyzer()
    return analyzer.run_a11y_analysis(url)


# Sync version for direct use
def run_a11y_sync(url: str) -> A11yReportSelenium:
    """
    Synchronous version of accessibility analysis
    """
    analyzer = SeleniumAccessibilityAnalyzer()
    return analyzer.run_a11y_analysis(url)


# Test function
def test_accessibility_analysis():
    """Test accessibility analysis"""
    try:
        url = "https://example.com"
        
        logger.info("Testing accessibility analysis with Selenium...")
        
        result = run_a11y_sync(url)
        
        print(f"Accessibility analysis completed in {result.processing_time:.2f}s")
        print(f"Total violations: {result.total_violations}")
        
        # Show first few issues
        for i, issue in enumerate(result.issues[:5]):
            print(f"{i+1}. {issue.internal_type}: {issue.message}")
            print(f"   Selector: {issue.selector}")
            print(f"   Impact: {issue.impact}")
            print()
            
        return result
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    # Run test
    test_accessibility_analysis()