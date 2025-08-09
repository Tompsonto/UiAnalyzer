"""
Accessibility Analysis Module using axe-core
Integrates with Playwright to run axe-core accessibility tests
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Page, Browser
import time

logger = logging.getLogger(__name__)


@dataclass
class A11yIssue:
    """Individual accessibility issue"""
    rule_id: str
    impact: str  # critical, serious, moderate, minor
    selector: str
    message: str
    internal_type: str  # contrast, landmark, label, alt, keyboard


@dataclass 
class A11yReport:
    """Complete accessibility analysis report"""
    issues: List[A11yIssue] = field(default_factory=list)
    violations_count: int = 0
    passes_count: int = 0
    incomplete_count: int = 0
    inapplicable_count: int = 0
    processing_time: float = 0


class AccessibilityRunner:
    """Runs axe-core accessibility tests using Playwright"""
    
    # Mapping from axe rule IDs to internal taxonomy
    AXE_TO_INTERNAL_MAPPING = {
        # Contrast rules
        'color-contrast': 'contrast',
        'color-contrast-enhanced': 'contrast',
        
        # Landmark rules
        'landmark-main-is-top-level': 'landmark',
        'landmark-no-duplicate-banner': 'landmark',
        'landmark-no-duplicate-contentinfo': 'landmark',
        'landmark-one-main': 'landmark',
        'page-has-heading-one': 'landmark',
        'region': 'landmark',
        
        # Label rules
        'label': 'label',
        'aria-label': 'label',
        'aria-labelledby': 'label',
        'form-field-multiple-labels': 'label',
        'input-button-name': 'label',
        'input-image-alt': 'label',
        
        # Alt text rules
        'image-alt': 'alt',
        'image-redundant-alt': 'alt',
        'object-alt': 'alt',
        'area-alt': 'alt',
        
        # Keyboard rules
        'accesskeys': 'keyboard',
        'tabindex': 'keyboard',
        'focus-order-semantics': 'keyboard',
        'focusable-content': 'keyboard',
    }
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None
        
    async def __aenter__(self):
        """Initialize Playwright context"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def run_a11y(self, url: str) -> A11yReport:
        """
        Run accessibility analysis on the given URL
        
        Args:
            url: URL to analyze
            
        Returns:
            A11yReport with accessibility issues
        """
        start_time = time.time()
        
        try:
            if not self.browser:
                raise RuntimeError("AccessibilityRunner not initialized. Use 'async with' context manager.")
            
            # Create new page
            page = await self.browser.new_page()
            
            try:
                # Navigate to URL
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Inject axe-core
                await self._inject_axe_core(page)
                
                # Run axe analysis
                axe_results = await self._run_axe_analysis(page)
                
                # Process results
                report = self._process_axe_results(axe_results)
                report.processing_time = time.time() - start_time
                
                return report
                
            finally:
                await page.close()
                
        except Exception as e:
            logger.error(f"Accessibility analysis failed for {url}: {str(e)}")
            return A11yReport(
                issues=[A11yIssue(
                    rule_id="analysis-error",
                    impact="critical", 
                    selector="body",
                    message=f"Accessibility analysis failed: {str(e)}",
                    internal_type="system"
                )],
                processing_time=time.time() - start_time
            )
    
    async def _inject_axe_core(self, page: Page):
        """Inject axe-core library into the page"""
        try:
            # Load axe-core from CDN
            await page.add_script_tag(url="https://unpkg.com/axe-core@4.8.2/axe.min.js")
            
            # Wait for axe to be available
            await page.wait_for_function("typeof axe !== 'undefined'", timeout=10000)
            
        except Exception as e:
            logger.error(f"Failed to inject axe-core: {str(e)}")
            raise
    
    async def _run_axe_analysis(self, page: Page) -> Dict[str, Any]:
        """Run axe accessibility analysis on the page"""
        try:
            # Configure axe options
            axe_config = {
                'rules': {
                    # Enable specific rules we care about
                    'color-contrast': {'enabled': True},
                    'color-contrast-enhanced': {'enabled': True},
                    'landmark-main-is-top-level': {'enabled': True},
                    'landmark-one-main': {'enabled': True},
                    'page-has-heading-one': {'enabled': True},
                    'region': {'enabled': True},
                    'label': {'enabled': True},
                    'aria-label': {'enabled': True},
                    'image-alt': {'enabled': True},
                    'input-button-name': {'enabled': True},
                    'accesskeys': {'enabled': True},
                    'tabindex': {'enabled': True},
                },
                'tags': ['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice']
            }
            
            # Run axe analysis
            result = await page.evaluate(f"""
                () => {{
                    return new Promise((resolve, reject) => {{
                        axe.run(document, {json.dumps(axe_config)}, (err, results) => {{
                            if (err) {{
                                reject(err);
                            }} else {{
                                resolve(results);
                            }}
                        }});
                    }});
                }}
            """)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to run axe analysis: {str(e)}")
            raise
    
    def _process_axe_results(self, axe_results: Dict[str, Any]) -> A11yReport:
        """Process axe results into our internal format"""
        issues = []
        
        # Process violations (actual issues)
        for violation in axe_results.get('violations', []):
            rule_id = violation.get('id', 'unknown')
            impact = violation.get('impact', 'moderate')
            description = violation.get('description', 'Accessibility issue detected')
            
            # Map to internal taxonomy
            internal_type = self.AXE_TO_INTERNAL_MAPPING.get(rule_id, 'other')
            
            # Process each node (element) that has this violation
            for node in violation.get('nodes', []):
                # Get the best selector available
                target = node.get('target', ['unknown'])
                selector = target[0] if isinstance(target, list) and target else 'unknown'
                
                # Get failure summary or use description
                failure_summary = node.get('failureSummary', description)
                
                issues.append(A11yIssue(
                    rule_id=rule_id,
                    impact=impact,
                    selector=selector,
                    message=self._create_user_friendly_message(rule_id, failure_summary, internal_type),
                    internal_type=internal_type
                ))
        
        return A11yReport(
            issues=issues,
            violations_count=len(axe_results.get('violations', [])),
            passes_count=len(axe_results.get('passes', [])),
            incomplete_count=len(axe_results.get('incomplete', [])),
            inapplicable_count=len(axe_results.get('inapplicable', []))
        )
    
    def _create_user_friendly_message(self, rule_id: str, failure_summary: str, internal_type: str) -> str:
        """Create user-friendly messages for accessibility issues"""
        
        # Custom messages based on rule type
        friendly_messages = {
            'color-contrast': 'Text color doesn\'t have enough contrast with background, making it hard to read',
            'color-contrast-enhanced': 'Text contrast doesn\'t meet enhanced accessibility standards',
            'landmark-main-is-top-level': 'Main content area should be a top-level landmark for screen readers',
            'landmark-one-main': 'Page should have exactly one main content area',
            'page-has-heading-one': 'Page is missing a main heading (H1) for structure and navigation',
            'region': 'Page content should be contained within landmark regions for screen readers',
            'label': 'Form element is missing a proper label for screen readers',
            'aria-label': 'Element needs an accessible name for screen readers',
            'image-alt': 'Image is missing alternative text for screen readers',
            'input-button-name': 'Button or input needs an accessible name',
            'accesskeys': 'Keyboard shortcuts (accesskey) may conflict or be problematic',
            'tabindex': 'Tab navigation order may be confusing or inaccessible',
        }
        
        # Use custom message if available, otherwise clean up the failure summary
        if rule_id in friendly_messages:
            return friendly_messages[rule_id]
        else:
            # Clean up technical failure summary
            return failure_summary.split('Fix any')[0].strip() if 'Fix any' in failure_summary else failure_summary


# Convenience function for easy usage
async def run_a11y(url: str) -> A11yReport:
    """
    Convenience function to run accessibility analysis
    
    Args:
        url: URL to analyze
        
    Returns:
        A11yReport with accessibility issues
    """
    async with AccessibilityRunner() as runner:
        return await runner.run_a11y(url)


# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Test with a sample URL
        test_url = "https://example.com"
        report = await run_a11y(test_url)
        
        print(f"Accessibility Report for {test_url}")
        print(f"Issues found: {len(report.issues)}")
        print(f"Violations: {report.violations_count}")
        print(f"Processing time: {report.processing_time:.2f}s")
        
        for issue in report.issues[:5]:  # Show first 5 issues
            print(f"\n- Rule: {issue.rule_id}")
            print(f"  Impact: {issue.impact}")
            print(f"  Type: {issue.internal_type}")
            print(f"  Element: {issue.selector}")
            print(f"  Issue: {issue.message}")
    
    asyncio.run(main())