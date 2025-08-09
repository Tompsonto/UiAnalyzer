"""
Tests for accessibility runner module
"""

import asyncio
import pytest
from pathlib import Path
import tempfile
import os
from app.modules.a11y_runner import AccessibilityRunner, run_a11y, A11yReport, A11yIssue


# Sample HTML with accessibility violations for testing
SAMPLE_HTML_WITH_VIOLATIONS = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page with A11y Issues</title>
    <style>
        .low-contrast { color: #ccc; background: #fff; }
        .very-low-contrast { color: #ddd; background: #fff; }
    </style>
</head>
<body>
    <!-- Missing H1 heading -->
    <h2>This should be H1</h2>
    
    <!-- Low contrast text -->
    <p class="low-contrast">This text has poor contrast ratio</p>
    <p class="very-low-contrast">This text has very poor contrast</p>
    
    <!-- Image without alt text -->
    <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" width="100" height="100">
    
    <!-- Input without label -->
    <form>
        <input type="text" placeholder="Enter your name">
        <button type="submit">Submit</button>
    </form>
    
    <!-- Content not in landmarks -->
    <div>
        <p>This content is not in proper landmark regions</p>
    </div>
</body>
</html>
"""


@pytest.fixture
def sample_html_file():
    """Create a temporary HTML file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(SAMPLE_HTML_WITH_VIOLATIONS)
        f.flush()
        file_path = f.name
    
    yield f"file://{file_path}"
    
    # Cleanup
    try:
        os.unlink(file_path)
    except OSError:
        pass


class TestAccessibilityRunner:
    """Test cases for AccessibilityRunner"""
    
    @pytest.mark.asyncio
    async def test_basic_functionality(self, sample_html_file):
        """Test basic accessibility analysis functionality"""
        async with AccessibilityRunner() as runner:
            report = await runner.run_a11y(sample_html_file)
            
            # Should be an A11yReport
            assert isinstance(report, A11yReport)
            
            # Should have some violations from our test HTML
            assert len(report.issues) > 0
            
            # Should have processing time
            assert report.processing_time > 0
    
    @pytest.mark.asyncio  
    async def test_expected_violations(self, sample_html_file):
        """Test that expected violations are detected"""
        async with AccessibilityRunner() as runner:
            report = await runner.run_a11y(sample_html_file)
            
            # Extract rule IDs from issues
            rule_ids = {issue.rule_id for issue in report.issues}
            internal_types = {issue.internal_type for issue in report.issues}
            
            # Should detect some of these common violations
            expected_violations = {
                'color-contrast',  # Low contrast text
                'image-alt',       # Missing alt text
                'label',          # Input without label
                'page-has-heading-one',  # Missing H1
                'region'          # Content not in landmarks
            }
            
            # Should detect at least some expected violations
            detected_violations = rule_ids & expected_violations
            assert len(detected_violations) >= 2, f"Expected violations but only found: {rule_ids}"
            
            # Should map to internal taxonomy
            expected_internal_types = {'contrast', 'alt', 'label', 'landmark'}
            detected_types = internal_types & expected_internal_types
            assert len(detected_types) >= 2, f"Expected internal types but only found: {internal_types}"
    
    @pytest.mark.asyncio
    async def test_issue_structure(self, sample_html_file):
        """Test that issues have proper structure"""
        async with AccessibilityRunner() as runner:
            report = await runner.run_a11y(sample_html_file)
            
            # Should have at least one issue
            assert len(report.issues) > 0
            
            # Check issue structure
            for issue in report.issues:
                assert isinstance(issue, A11yIssue)
                assert issue.rule_id  # Should have rule ID
                assert issue.impact in ['critical', 'serious', 'moderate', 'minor']
                assert issue.selector  # Should have element selector
                assert issue.message   # Should have user-friendly message
                assert issue.internal_type  # Should be mapped to internal taxonomy
    
    @pytest.mark.asyncio
    async def test_internal_type_mapping(self, sample_html_file):
        """Test mapping from axe rules to internal taxonomy"""
        async with AccessibilityRunner() as runner:
            report = await runner.run_a11y(sample_html_file)
            
            # Check that internal types are valid
            valid_internal_types = {'contrast', 'landmark', 'label', 'alt', 'keyboard', 'other', 'system'}
            
            for issue in report.issues:
                assert issue.internal_type in valid_internal_types, f"Invalid internal type: {issue.internal_type}"
    
    @pytest.mark.asyncio
    async def test_user_friendly_messages(self, sample_html_file):
        """Test that messages are user-friendly"""
        async with AccessibilityRunner() as runner:
            report = await runner.run_a11y(sample_html_file)
            
            for issue in report.issues:
                # Messages should be reasonably descriptive
                assert len(issue.message) > 10
                
                # Should not contain technical jargon like "Fix any of the following"
                assert "Fix any of the following" not in issue.message
                
                # Should be human readable (contains spaces)
                assert " " in issue.message
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for invalid URLs"""
        async with AccessibilityRunner() as runner:
            # Test with invalid URL
            report = await runner.run_a11y("invalid-url")
            
            # Should return error report
            assert len(report.issues) == 1
            assert report.issues[0].rule_id == "analysis-error"
            assert report.issues[0].impact == "critical"
    
    @pytest.mark.asyncio
    async def test_convenience_function(self, sample_html_file):
        """Test the convenience function"""
        report = await run_a11y(sample_html_file)
        
        assert isinstance(report, A11yReport)
        assert len(report.issues) > 0


class TestA11yDataStructures:
    """Test data structures used in accessibility analysis"""
    
    def test_a11y_issue_creation(self):
        """Test A11yIssue creation"""
        issue = A11yIssue(
            rule_id="color-contrast",
            impact="serious", 
            selector="p.low-contrast",
            message="Text has poor contrast",
            internal_type="contrast"
        )
        
        assert issue.rule_id == "color-contrast"
        assert issue.impact == "serious"
        assert issue.selector == "p.low-contrast"
        assert issue.message == "Text has poor contrast"
        assert issue.internal_type == "contrast"
    
    def test_a11y_report_creation(self):
        """Test A11yReport creation"""
        issues = [
            A11yIssue("rule1", "high", "selector1", "message1", "contrast"),
            A11yIssue("rule2", "medium", "selector2", "message2", "alt")
        ]
        
        report = A11yReport(
            issues=issues,
            violations_count=2,
            passes_count=10,
            processing_time=1.5
        )
        
        assert len(report.issues) == 2
        assert report.violations_count == 2
        assert report.passes_count == 10
        assert report.processing_time == 1.5


if __name__ == "__main__":
    # Run a simple test
    async def simple_test():
        print("Running simple accessibility test...")
        
        # Create sample HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(SAMPLE_HTML_WITH_VIOLATIONS)
            f.flush()
            file_url = f"file://{f.name}"
        
        try:
            report = await run_a11y(file_url)
            print(f"Found {len(report.issues)} accessibility issues")
            print(f"Violations: {report.violations_count}, Passes: {report.passes_count}")
            
            for issue in report.issues[:3]:  # Show first 3
                print(f"- {issue.internal_type}: {issue.message}")
                
        finally:
            os.unlink(f.name)
    
    asyncio.run(simple_test())